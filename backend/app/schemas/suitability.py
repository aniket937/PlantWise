"""Suitability analysis request/response contract.

The response is intentionally explicit about *what was compared*, so the UI can
show reasoning rather than an unexplained verdict.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator

from app.schemas.common import ApiModel, DataSource
from app.schemas.plant import PlantSummary, RegionSummary

CriterionStatus = Literal["pass", "caution", "fail", "unknown"]
AssessmentStatus = Literal[
    "suitable", "potentially_suitable", "not_supported", "insufficient_data"
]
ConfidenceLabel = Literal["high", "moderate", "low", "none"]
SoilType = Literal["sandy", "loam", "clay", "silt", "chalky"]
SunlightInput = Literal["full_sun", "partial_sun", "partial_shade", "full_shade"]
IrrigationLevel = Literal["none", "occasional", "regular", "abundant"]


class GrowingInputs(ApiModel):
    """Optional local context. Every field is genuinely optional."""

    soil_type: SoilType | None = None
    sunlight: SunlightInput | None = None
    irrigation: IrrigationLevel | None = None


class LocationInput(ApiModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    label: str | None = Field(default=None, max_length=200)
    name: str | None = Field(default=None, max_length=160)
    country: str | None = Field(default=None, max_length=120)
    country_code: str | None = Field(default=None, max_length=3)
    admin_area: str | None = Field(default=None, max_length=160)
    timezone: str | None = Field(default=None, max_length=80)


class SuitabilityRequest(ApiModel):
    plant_slug: str = Field(min_length=2, max_length=80)
    location: LocationInput | None = None
    place_query: str | None = Field(default=None, min_length=2, max_length=160)
    growing_inputs: GrowingInputs = Field(default_factory=GrowingInputs)

    @model_validator(mode="after")
    def _require_a_location(self) -> "SuitabilityRequest":
        if self.location is None and not (self.place_query or "").strip():
            raise ValueError(
                "Provide either 'location' coordinates or a 'place_query' to analyse."
            )
        return self


class ResolvedLocation(ApiModel):
    label: str
    latitude: float
    longitude: float
    country: str | None = None
    country_code: str | None = None
    admin_area: str | None = None
    timezone: str | None = None
    source: str


class CriterionResult(ApiModel):
    key: str
    label: str
    status: CriterionStatus
    requirement: str
    observed: str | None = None
    explanation: str
    weight: float = 1.0
    source: DataSource | None = None


class Confidence(ApiModel):
    value: float = Field(ge=0.0, le=1.0)
    label: ConfidenceLabel
    evaluated: int
    total: int
    methodology: str


class Assessment(ApiModel):
    status: AssessmentStatus
    label: str
    headline: str
    summary: str
    confidence: Confidence


class MonthClimate(ApiModel):
    month: str
    month_index: int
    mean_min_c: float
    mean_max_c: float
    precipitation_mm: float


class MonthExtreme(ApiModel):
    month: str
    month_index: int
    value_c: float


class ClimateSnapshot(ApiModel):
    available: bool
    source: str
    baseline: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    elevation_m: float | None = None
    annual_mean_min_c: float | None = None
    annual_mean_max_c: float | None = None
    coldest_month: MonthExtreme | None = None
    hottest_month: MonthExtreme | None = None
    annual_precipitation_mm: float | None = None
    frost_days_per_year: int | None = None
    growing_degree_days_base10: float | None = None
    monthly: list[MonthClimate] = Field(default_factory=list)
    unavailable_reason: str | None = None


class CultivationEvidence(ApiModel):
    available: bool
    regions: list[RegionSummary] = Field(default_factory=list)
    note: str


class NextStep(ApiModel):
    title: str
    detail: str


class GeneratedExplanation(ApiModel):
    """Model-generated narrative, always kept separate from the verdict."""

    available: bool
    model: str | None = None
    text: str | None = None
    unavailable_reason: str | None = None


class SuitabilityResponse(ApiModel):
    plant: PlantSummary
    location: ResolvedLocation
    assessment: Assessment
    climate: ClimateSnapshot
    criteria: list[CriterionResult] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    next_steps: list[NextStep] = Field(default_factory=list)
    cultivation_evidence: CultivationEvidence
    generated_explanation: GeneratedExplanation | None = None
    methodology_version: str
    evaluated_at: datetime
