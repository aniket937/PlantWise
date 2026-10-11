"""Hosted AI assistant endpoints.

The assistant is optional by design. When no OpenRouter key is configured (or
the service cannot be reached), this returns a clean ``available: false``
payload with the reason, so the interface can say so plainly instead of failing
or faking a reply.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.schemas.assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantContext,
    AssistantStatusResponse,
)
from app.services import ai
from app.services.plants import get_by_slug

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.get(
    "/status",
    response_model=AssistantStatusResponse,
    summary="Is the hosted model runtime reachable?",
)
async def status() -> AssistantStatusResponse:
    available, detail = await ai.check_availability()
    return AssistantStatusResponse(
        available=available,
        model=settings.openrouter_model,
        base_url_configured=ai.is_configured(),
        detail=detail,
        checked_at=ai.status_checked_at(),
    )


@router.post(
    "/chat",
    response_model=AssistantChatResponse,
    summary="Ask the hosted model a growing question",
)
async def chat(
    payload: AssistantChatRequest,
    session: AsyncSession = Depends(get_session),
) -> AssistantChatResponse:
    plant = None
    if payload.plant_slug:
        plant = await get_by_slug(session, payload.plant_slug)

    location_label = None
    if payload.location is not None:
        location_label = (
            payload.location.label
            or payload.location.name
            or f"{payload.location.latitude:.3f}, {payload.location.longitude:.3f}"
        )

    context = AssistantContext(
        plant_slug=plant.slug if plant else None,
        plant_common_name=plant.common_name if plant else None,
        plant_scientific_name=plant.scientific_name if plant else None,
        location_label=location_label,
        applied=plant is not None or location_label is not None,
    )

    outcome = await ai.chat(payload.messages, plant=plant, location_label=location_label)

    return AssistantChatResponse(
        available=outcome.available,
        reply=outcome.reply,
        model=outcome.model,
        unavailable_reason=outcome.unavailable_reason,
        disclaimer=ai.DISCLAIMER,
        context=context,
        latency_ms=outcome.latency_ms,
    )
