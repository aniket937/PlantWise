"""Geocoding schemas."""

from __future__ import annotations

from pydantic import Field

from app.schemas.common import ApiModel


class GeocodedLocation(ApiModel):
    label: str
    name: str
    latitude: float
    longitude: float
    country: str | None = None
    country_code: str | None = None
    admin_area: str | None = None
    admin_area_2: str | None = None
    timezone: str | None = None
    population: int | None = None
    source: str


class LocationSearchResponse(ApiModel):
    query: str
    provider: str
    results: list[GeocodedLocation] = Field(default_factory=list)
    unavailable_reason: str | None = None
