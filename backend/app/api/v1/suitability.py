"""Suitability analysis endpoint.

The verdict is produced by the deterministic engine in ``app.services.suitability``.
The language model is optional and, when used, only ever *narrates* the result the
engine already computed; it never decides the outcome.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ResourceNotFoundError
from app.db.session import get_session
from app.schemas.assistant import ChatMessage
from app.schemas.suitability import (
    GeneratedExplanation,
    LocationInput,
    ResolvedLocation,
    SuitabilityRequest,
    SuitabilityResponse,
)
from app.services import ai
from app.services.climate import get_climate_snapshot
from app.services.geocoding import geocode_one
from app.services.plants import bump_popularity, get_by_slug, to_summary
from app.services.suitability import analyse_suitability

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/suitability", tags=["suitability"])


def _resolve_location(
    location: LocationInput | None, place_query: str | None
) -> ResolvedLocation | None:
    if location is None:
        return None
    label = (
        location.label
        or location.name
        or f"{location.latitude:.4f}, {location.longitude:.4f}"
    )
    return ResolvedLocation(
        label=label,
        latitude=location.latitude,
        longitude=location.longitude,
        country=location.country,
        country_code=location.country_code,
        admin_area=location.admin_area,
        timezone=location.timezone,
        source="Supplied by the client",
    )


async def _resolve_place(place_query: str) -> ResolvedLocation:
    found = await geocode_one(place_query)
    if found is None:
        raise ResourceNotFoundError(
            "That place could not be found. Try a nearby larger town or city.",
            code="place_not_found",
        )
    return ResolvedLocation(
        label=found.label,
        latitude=found.latitude,
        longitude=found.longitude,
        country=found.country,
        country_code=found.country_code,
        admin_area=found.admin_area,
        timezone=found.timezone,
        source=found.source,
    )


def _explanation_prompt(response: SuitabilityResponse) -> str:
    lines = [
        f"Explain this plant-growing assessment in plain language for a grower.",
        f"Plant: {response.plant.common_name} ({response.plant.scientific_name})",
        f"Place: {response.location.label}",
        f"Engine verdict: {response.assessment.headline}",
        f"Engine summary: {response.assessment.summary}",
        "Criteria the engine evaluated:",
    ]
    for criterion in response.criteria:
        lines.append(
            f"- {criterion.label}: {criterion.status}. Requirement: {criterion.requirement}. "
            f"Observed: {criterion.observed or 'not available'}. {criterion.explanation}"
        )
    lines.append(
        "Write two or three short paragraphs. Do not change the verdict or invent figures. "
        "Do not give a numeric suitability score. Focus on what the grower should do next."
    )
    return "\n".join(lines)


@router.post(
    "",
    response_model=SuitabilityResponse,
    summary="Assess how well a plant's requirements match a location's climate",
)
async def assess(
    payload: SuitabilityRequest,
    explain: bool = Query(
        default=False,
        description="Also ask the hosted model to narrate the result. Never changes the verdict.",
    ),
    session: AsyncSession = Depends(get_session),
) -> SuitabilityResponse:
    plant = await get_by_slug(session, payload.plant_slug)
    if plant is None:
        raise ResourceNotFoundError(
            f"No plant profile matches '{payload.plant_slug}'.",
            code="plant_not_found",
        )

    resolved = _resolve_location(payload.location, payload.place_query)
    if resolved is None:
        resolved = await _resolve_place(payload.place_query or "")

    climate = await get_climate_snapshot(session, resolved.latitude, resolved.longitude)
    response = await analyse_suitability(
        session, plant, resolved, payload.growing_inputs, climate=climate
    )

    await bump_popularity(session, plant)
    await session.commit()

    if explain:
        outcome = await ai.chat(
            [ChatMessage(role="user", content=_explanation_prompt(response))],
            plant=plant,
            location_label=resolved.label,
        )
        response.generated_explanation = GeneratedExplanation(
            available=outcome.available,
            model=outcome.model,
            text=outcome.reply,
            unavailable_reason=outcome.unavailable_reason,
        )

    response.plant = to_summary(plant)
    return response
