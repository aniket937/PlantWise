"""Farming-regions schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import ApiModel
from app.schemas.plant import PlantSummary, RegionSummary


class MapMarker(ApiModel):
    slug: str
    name: str
    country: str
    latitude: float
    longitude: float
    evidence_type: str


class RegionMapConfig(ApiModel):
    available: bool
    tile_url: str | None = None
    attribution: str | None = None
    default_center: tuple[float, float]
    default_zoom: int
    detail: str


class PlantRegionsResponse(ApiModel):
    plant: PlantSummary
    regions: list[RegionSummary] = Field(default_factory=list)
    markers: list[MapMarker] = Field(default_factory=list)
    map: RegionMapConfig
    notes: list[str] = Field(default_factory=list)
    generated_at: datetime


class RegionPlantOption(ApiModel):
    slug: str
    common_name: str
    scientific_name: str
    image_url: str | None = None
    region_count: int = 0


class RegionPlantListResponse(ApiModel):
    items: list[RegionPlantOption]
