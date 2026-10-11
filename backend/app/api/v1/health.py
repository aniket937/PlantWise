"""Health and capability reporting.

The frontend uses this to decide what to show as unavailable instead of
pretending a feature works.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.assistant import AssistantStatusResponse
from app.services import ai
from app.services.seed import plant_count
from app.db.session import SessionFactory

router = APIRouter(tags=["health"])


@router.get("/health", summary="Service health and capability report")
async def health() -> dict:
    assistant_available, assistant_detail = await ai.check_availability()

    database_ok = True
    database_detail = "Connected"
    plants = 0
    try:
        async with SessionFactory() as session:
            plants = await plant_count(session)
    except Exception:  # noqa: BLE001 - health must always answer
        database_ok = False
        database_detail = "The database could not be queried."

    return {
        "status": "ok" if database_ok else "degraded",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "capabilities": {
            "plants": {
                "available": plants > 0,
                "detail": f"{plants} plant profiles available." if plants else "No profiles are seeded yet.",
            },
            "suitability": {
                "available": True,
                "detail": "Climate comparisons run against the Open-Meteo historical archive.",
            },
            "assistant": {
                "available": assistant_available,
                "model": settings.openrouter_model,
                "detail": assistant_detail,
            },
        },
        "database": {"available": database_ok, "detail": database_detail},
    }


@router.get(
    "/health/assistant",
    response_model=AssistantStatusResponse,
    summary="Whether the hosted AI assistant is reachable",
)
async def assistant_health() -> AssistantStatusResponse:
    available, detail = await ai.check_availability()
    return AssistantStatusResponse(
        available=available,
        model=settings.openrouter_model,
        base_url_configured=ai.is_configured(),
        detail=detail,
        checked_at=ai.status_checked_at(),
    )
