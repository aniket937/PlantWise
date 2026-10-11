"""Consistent error envelope shared by every API route."""

from __future__ import annotations

from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

ERROR_ENVELOPE_EXAMPLE: dict[str, Any] = {
    "error": {
        "code": "plant_not_found",
        "message": "No plant matched slug 'tomatoe'.",
        "details": None,
    }
}


class PlantWiseError(Exception):
    """Base class for expected, user-facing failures."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "bad_request"

    def __init__(
        self,
        message: str,
        *,
        details: Any | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details
        if code is not None:
            self.code = code


class ResourceNotFoundError(PlantWiseError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class UpstreamServiceError(PlantWiseError):
    """An external provider (climate, geocoding, model runtime) failed."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "upstream_unavailable"


class InvalidRequestError(PlantWiseError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "invalid_request"


def error_body(code: str, message: str, details: Any | None = None) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details}}


async def plantwise_error_handler(_: Request, exc: Exception) -> JSONResponse:
    """Handler for expected, user-facing failures.

    Typed on ``Exception`` to match Starlette's handler protocol; anything that
    is not a PlantWiseError falls through to a generic 500 envelope rather than
    leaking internals.
    """
    if not isinstance(exc, PlantWiseError):  # pragma: no cover - defensive
        return JSONResponse(
            status_code=500,
            content=error_body(
                "internal_error",
                "Something went wrong on the server. The request was not completed.",
            ),
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.code, exc.message, exc.details),
    )


async def validation_error_handler(_: Request, exc: Exception) -> JSONResponse:
    """Return the same envelope for Pydantic failures, minus internal noise."""
    if not isinstance(exc, RequestValidationError):  # pragma: no cover - defensive
        return JSONResponse(
            status_code=422,
            content=error_body("validation_error", "The request payload failed validation."),
        )
    details = [
        {
            "field": ".".join(str(part) for part in error.get("loc", ())[1:]) or "(body)",
            "message": error.get("msg", "Invalid value"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=error_body(
            "validation_error", "The request payload failed validation.", details
        ),
    )
