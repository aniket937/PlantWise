"""Plant profile schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.schemas.common import ApiModel, DataSource

Lifecycle = Literal["annual", "biennial", "perennial"]
Difficulty = Literal["beginner", "intermediate", "advanced"]
WaterRequirement = Literal["low", "moderate", "high"]
SunlightRequirement = Literal["full_sun", "partial_sun", "partial_shade", "full_shade"]
FrostTolerance = Literal["none", "light", "moderate", "high"]
EvidenceType = Literal["documented_cultivation", "inferred_suitability"]


class RegionSummary(ApiModel):
    slug: str
    name: str
    country: str
    country_code: str | None = None
    admin_area: str | None = None
    latitude: float
    longitude: float
    evidence_type: EvidenceType
    description: str | None = None
    climate_note: str | None = None
    rank: int = 100
    data_sources: list[DataSource] = Field(default_factory=list)


class TemperatureProfile(ApiModel):
    min_c: float | None = None
    max_c: float | None = None
    optimal_min_c: float | None = None
    optimal_max_c: float | None = None
    frost_tolerance: FrostTolerance | None = None
    notes: str | None = None
    source: DataSource | None = None


class RainfallProfile(ApiModel):
    min_mm: float | None = None
    max_mm: float | None = None
    notes: str | None = None
    source: DataSource | None = None


class SoilProfile(ApiModel):
    textures: list[str] = Field(default_factory=list)
    ph_min: float | None = None
    ph_max: float | None = None
    drainage: str | None = None
    notes: str | None = None
    source: DataSource | None = None


class WaterProfile(ApiModel):
    requirement: WaterRequirement | None = None
    notes: str | None = None
    source: DataSource | None = None


class SunlightProfile(ApiModel):
    requirement: SunlightRequirement | None = None
    hours_min: float | None = None
    notes: str | None = None
    source: DataSource | None = None


class GrowingSeason(ApiModel):
    days_min: int | None = None
    days_max: int | None = None
    notes: str | None = None


class CultivationStep(ApiModel):
    order: int
    title: str
    detail: str


class CommonProblem(ApiModel):
    name: str
    description: str


class PlantSummary(ApiModel):
    slug: str
    common_name: str
    scientific_name: str
    family: str | None = None
    short_description: str
    image_url: str | None = None
    image_attribution: str | None = None
    image_license: str | None = None
    image_source_url: str | None = None
    lifecycle: Lifecycle | None = None
    growth_habit: str | None = None
    difficulty: Difficulty | None = None
    tags: list[str] = Field(default_factory=list)
    data_sources: list[DataSource] = Field(default_factory=list)


class PlantDetail(PlantSummary):
    description: str | None = None
    temperature: TemperatureProfile
    rainfall: RainfallProfile
    soil: SoilProfile
    water: WaterProfile
    sunlight: SunlightProfile
    growing_season: GrowingSeason
    cultivation_steps: list[CultivationStep] = Field(default_factory=list)
    common_problems: list[CommonProblem] = Field(default_factory=list)
    regions: list[RegionSummary] = Field(default_factory=list)
    popularity: int = 0


class PlantListResponse(ApiModel):
    items: list[PlantSummary]
    total: int
    query: str | None = None
    suggestions: list[str] = Field(default_factory=list)


class PlantCollection(ApiModel):
    """Curated home-page collections, each with the reason it is being shown."""

    popular: list[PlantSummary] = Field(default_factory=list)
    popular_note: str = "Most viewed profiles on this instance so far."
    recent: list[PlantSummary] = Field(default_factory=list)
    recent_note: str = "Profiles people looked at most recently."
    total: int = 0
