"""Place search for the location picker."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.errors import InvalidRequestError
from app.schemas.location import LocationSearchResponse
from app.services.geocoding import geocoder_name, search_locations

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get(
    "/search",
    response_model=LocationSearchResponse,
    summary="Find coordinates for a place name",
)
async def search(
    q: str = Query(min_length=2, max_length=160, description="Place name, e.g. 'Nairobi'"),
    limit: int = Query(default=6, ge=1, le=20),
) -> LocationSearchResponse:
    query = q.strip()
    if len(query) < 2:
        raise InvalidRequestError(
            "Enter at least two characters to search for a place.", code="query_too_short"
        )

    try:
        results = await search_locations(query, limit=limit)
    except Exception:  # noqa: BLE001 - surfaced as a soft, renderable state
        return LocationSearchResponse(
            query=query,
            provider=geocoder_name(),
            results=[],
            unavailable_reason=(
                "The place search service could not be reached. You can still enter "
                "coordinates directly."
            ),
        )
    return LocationSearchResponse(
        query=query,
        provider=geocoder_name(),
        results=results,
        unavailable_reason=None
        if results
        else "No places matched that search. Try a nearby larger town or a postcode.",
    )
