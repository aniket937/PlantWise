"""FastAPI application entrypoint.

Startup is tolerant: the API always boots, even when the local model runtime is
absent or the climate provider is unreachable. Those become reported capability
states rather than crashes.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import (
    PlantWiseError,
    error_body,
    plantwise_error_handler,
    validation_error_handler,
)
from app.db.session import SessionFactory, init_models
from app.services import ai
from app.services.seed import seed_database

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger("plantwise")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_models()
    logger.info("Database schema ready at %s", settings.database_url)

    if settings.seed_on_startup:
        try:
            async with SessionFactory() as session:
                result = await seed_database(session)
                await session.commit()
            logger.info(
                "Seed complete: %d plants inserted, %d refreshed",
                result.inserted,
                result.updated,
            )
        except Exception:  # noqa: BLE001 - seeding must not stop the API
            logger.exception("Seeding failed; the API will start without seed data")

    available, detail = await ai.check_availability()
    if available:
        logger.info("Assistant ready: %s", detail)
    else:
        logger.warning("Assistant unavailable: %s", detail)

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    summary=(
        "Plant discovery and location-based growing suitability, with a hosted "
        "open-weight AI assistant served through OpenRouter."
    ),
    description=(
        "Suitability verdicts come from a deterministic engine that compares published "
        "crop requirements against multi-year climatological normals. No numeric suitability "
        "percentage is produced; confidence reports how much of the comparison could actually "
        "be evaluated. Where a provider is unavailable the API says so instead of guessing."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

app.add_exception_handler(PlantWiseError, plantwise_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Never leak a stack trace; always return the shared envelope."""
    logger.exception("Unhandled error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=error_body(
            "internal_error",
            "Something went wrong on the server. The request was not completed.",
        ),
    )


app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["health"], summary="Service root")
async def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "api": settings.api_v1_prefix,
    }
