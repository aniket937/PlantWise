"""PlantWise suitability engine.

Methodology (version 1.0.0)
---------------------------
Each *applicable* criterion compares one published crop requirement against one
climatological normal derived from a multi-year daily reanalysis baseline. A
criterion is only applicable when both sides are actually known; anything else is
reported as ``unknown`` and named in the limitations, so a missing input can
never be silently treated as a pass.

Weights express how strongly a criterion constrains the verdict, not probability:

    cold_temperature  1.0   killing cold
    heat_temperature  1.0   heat that prevents fruiting or growth
    water_balance     1.0   seasonal water available vs. needed
    frost_risk        0.8   how often frost occurs vs. tolerance
    growing_window    0.8   months warm enough vs. season length needed
    soil_match        0.6   user-supplied soil texture vs. preference
    sunlight_match    0.5   user-supplied exposure vs. requirement

``confidence`` is the weighted share of applicable criteria that could be
evaluated. It is a measure of **evidence coverage**, deliberately *not* a
probability of success, and no numeric suitability percentage is produced.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Plant
from app.schemas.common import DataSource
from app.schemas.plant import RegionSummary
from app.schemas.suitability import (
    Assessment,
    ClimateSnapshot,
    Confidence,
    CriterionResult,
    CultivationEvidence,
    GrowingInputs,
    NextStep,
    ResolvedLocation,
    SuitabilityResponse,
)
from app.services.climate import get_climate_snapshot

METHODOLOGY_VERSION = "1.0.0"

WEIGHTS: dict[str, float] = {
    "cold_temperature": 1.0,
    "heat_temperature": 1.0,
    "water_balance": 1.0,
    "frost_risk": 0.8,
    "growing_window": 0.8,
    "soil_match": 0.6,
    "sunlight_match": 0.5,
}

ORDINAL_SUNLIGHT = ["full_shade", "partial_shade", "partial_sun", "full_sun"]

SUNLIGHT_LABEL = {
    "full_sun": "Full sun",
    "partial_sun": "Partial sun",
    "partial_shade": "Partial shade",
    "full_shade": "Full shade",
}

IRRIGATION_LABEL = {
    "none": "no irrigation",
    "occasional": "occasional irrigation",
    "regular": "regular irrigation",
    "abundant": "abundant irrigation",
}

FROST_TOLERANCE_DAYS = {"none": 0, "light": 20, "moderate": 60, "high": 150}

STATUS_LABEL = {
    "suitable": "Suitable based on available data",
    "potentially_suitable": "Potentially suitable, with limitations",
    "not_supported": "Not currently supported by the available conditions",
    "insufficient_data": "Insufficient data for a reliable assessment",
}


def _requirement_source(plant: Plant) -> DataSource | None:
    sources = plant.data_sources or []
    for entry in sources:
        if isinstance(entry, dict) and entry.get("url"):
            return DataSource(
                label=str(entry.get("label", "Reference")),
                url=entry.get("url"),
                note=entry.get("note"),
            )
    return None


def _fmt(value: float | None, unit: str = "") -> str:
    if value is None:
        return "unknown"
    return f"{value:g}{unit}"


def _unknown(key: str, label: str, requirement: str, explanation: str) -> CriterionResult:
    return CriterionResult(
        key=key,
        label=label,
        status="unknown",
        requirement=requirement,
        observed=None,
        explanation=explanation,
        weight=WEIGHTS[key],
    )


# ---------------------------------------------------------------- criteria


def _cold_temperature(plant: Plant, climate: ClimateSnapshot) -> CriterionResult:
    key = "cold_temperature"
    requirement = f"Coldest month mean minimum at or above {_fmt(plant.temp_min_c, ' °C')}"
    if plant.temp_min_c is None:
        return _unknown(key, "Cold-season temperature", requirement,
                        "This plant profile does not record a minimum temperature tolerance.")
    if not climate.available or climate.coldest_month is None:
        return _unknown(key, "Cold-season temperature", requirement,
                        "No climate baseline was available to compare against.")

    observed = climate.coldest_month.value_c
    margin = observed - plant.temp_min_c
    if margin >= 0:
        status, state = "pass", "meets the requirement"
    elif margin >= -2:
        status, state = "caution", "is marginally below the requirement"
    else:
        status, state = "fail", "is below the requirement"
    return CriterionResult(
        key=key,
        label="Cold-season temperature",
        status=status,  # type: ignore[arg-type]
        requirement=requirement,
        observed=f"{_fmt(observed, ' °C')} in {climate.coldest_month.month}",
        explanation=(
            f"The coldest month averages a minimum of {_fmt(observed, ' °C')}, which {state} "
            f"of {_fmt(plant.temp_min_c, ' °C')}."
        ),
        weight=WEIGHTS[key],
        source=_requirement_source(plant),
    )


def _heat_temperature(plant: Plant, climate: ClimateSnapshot) -> CriterionResult:
    key = "heat_temperature"
    requirement = f"Hottest month mean maximum at or below {_fmt(plant.temp_max_c, ' °C')}"
    if plant.temp_max_c is None:
        return _unknown(key, "Heat tolerance", requirement,
                        "This plant profile does not record a maximum temperature tolerance.")
    if not climate.available or climate.hottest_month is None:
        return _unknown(key, "Heat tolerance", requirement,
                        "No climate baseline was available to compare against.")

    observed = climate.hottest_month.value_c
    margin = plant.temp_max_c - observed
    if margin >= 0:
        status, state = "pass", "stays within the plant's tolerance"
    elif margin >= -2:
        status, state = "caution", "slightly exceeds the plant's tolerance"
    else:
        status, state = "fail", "exceeds the plant's tolerance"
    return CriterionResult(
        key=key,
        label="Heat tolerance",
        status=status,  # type: ignore[arg-type]
        requirement=requirement,
        observed=f"{_fmt(observed, ' °C')} in {climate.hottest_month.month}",
        explanation=(
            f"The hottest month averages a maximum of {_fmt(observed, ' °C')}, which {state} "
            f"of {_fmt(plant.temp_max_c, ' °C')}."
        ),
        weight=WEIGHTS[key],
        source=_requirement_source(plant),
    )


def _frost_risk(plant: Plant, climate: ClimateSnapshot) -> CriterionResult:
    key = "frost_risk"
    tolerance = plant.frost_tolerance
    if tolerance is None:
        return _unknown(key, "Frost exposure", "Frost tolerance not recorded",
                        "This plant profile does not record frost tolerance.")
    allowed = FROST_TOLERANCE_DAYS.get(tolerance, 0)
    requirement = (
        "No frost days in an average year"
        if allowed == 0
        else f"Up to about {allowed} frost days per year"
    )
    if not climate.available or climate.frost_days_per_year is None:
        return _unknown(key, "Frost exposure", requirement,
                        "No climate baseline was available to compare against.")

    days = climate.frost_days_per_year
    if days <= allowed:
        status, state = "pass", "within"
    elif days <= max(allowed * 2, allowed + 5):
        status, state = "caution", "above"
    else:
        status, state = "fail", "well above"
    return CriterionResult(
        key=key,
        label="Frost exposure",
        status=status,  # type: ignore[arg-type]
        requirement=requirement,
        observed=f"{days} frost days per year on average",
        explanation=(
            f"An average year has {days} days with a minimum below 0 °C, which is {state} "
            f"the recorded frost tolerance of this plant ({tolerance})."
        ),
        weight=WEIGHTS[key],
        source=_requirement_source(plant),
    )


def _growing_window(plant: Plant, climate: ClimateSnapshot) -> CriterionResult:
    key = "growing_window"
    if plant.growing_season_days_min is None:
        return _unknown(key, "Length of the growing window",
                        "Season length not recorded",
                        "This profile does not record a season length, which is expected for perennials.")
    threshold = plant.temp_min_c if plant.temp_min_c is not None else 5.0
    needed_months = max(1, math.ceil(plant.growing_season_days_min / 30.4))
    requirement = (
        f"At least {needed_months} months with a mean minimum of {_fmt(threshold, ' °C')} or more"
    )
    if not climate.available or not climate.monthly:
        return _unknown(key, "Length of the growing window", requirement,
                        "No monthly climate baseline was available to compare against.")

    window = sum(1 for month in climate.monthly if month.mean_min_c >= threshold)
    if window >= needed_months:
        status, state = "pass", "reaches"
    elif window >= needed_months - 1:
        status, state = "caution", "just misses"
    else:
        status, state = "fail", "falls short of"
    return CriterionResult(
        key=key,
        label="Length of the growing window",
        status=status,  # type: ignore[arg-type]
        requirement=requirement,
        observed=f"{window} of 12 months meet that threshold",
        explanation=(
            f"{window} months of the year are warm enough for this crop, which {state} the "
            f"{needed_months} months a minimum-length season needs."
        ),
        weight=WEIGHTS[key],
        source=_requirement_source(plant),
    )


def _water_balance(
    plant: Plant, climate: ClimateSnapshot, growing: GrowingInputs
) -> CriterionResult:
    key = "water_balance"
    lo, hi = plant.rainfall_min_mm, plant.rainfall_max_mm
    if lo is None or hi is None:
        return _unknown(key, "Water availability",
                        "Rainfall requirement not recorded",
                        "This plant profile does not record a rainfall requirement.")
    requirement = f"{_fmt(lo, ' mm')} to {_fmt(hi, ' mm')} of precipitation per year"
    if not climate.available or climate.annual_precipitation_mm is None:
        return _unknown(key, "Water availability", requirement,
                        "No precipitation baseline was available to compare against.")

    actual = climate.annual_precipitation_mm
    irrigation = growing.irrigation
    irrigated = irrigation in ("regular", "abundant")
    irrigation_text = (
        f" The location is marked as having {IRRIGATION_LABEL[irrigation]}."
        if irrigation
        else " No irrigation was declared, so this assumes the crop relies on rainfall alone."
    )

    if lo <= actual <= hi:
        status = "pass"
        explanation = (
            f"Annual precipitation of {_fmt(actual, ' mm')} falls inside the recorded "
            f"requirement of {_fmt(lo, ' mm')} to {_fmt(hi, ' mm')}.{irrigation_text}"
        )
    elif actual < lo:
        deficit = (lo - actual) / lo
        if irrigated:
            status = "pass"
            explanation = (
                f"Annual precipitation of {_fmt(actual, ' mm')} is below the "
                f"{_fmt(lo, ' mm')} minimum, a shortfall of about {deficit * 100:.0f}%. "
                f"Because {IRRIGATION_LABEL[irrigation]} is declared for this site, the gap "
                "can be met with water."
            )
        elif deficit > 0.6:
            status = "fail"
            explanation = (
                f"Annual precipitation of {_fmt(actual, ' mm')} is about "
                f"{deficit * 100:.0f}% below the recorded minimum of {_fmt(lo, ' mm')}. "
                f"That is a large deficit.{irrigation_text}"
            )
        else:
            status = "caution"
            explanation = (
                f"Annual precipitation of {_fmt(actual, ' mm')} is about "
                f"{deficit * 100:.0f}% below the recorded minimum of {_fmt(lo, ' mm')}. "
                f"Supplementary water would be needed.{irrigation_text}"
            )
    else:
        status = "caution"
        explanation = (
            f"Annual precipitation of {_fmt(actual, ' mm')} is above the recorded upper "
            f"range of {_fmt(hi, ' mm')}. Excess water raises drainage and disease pressure, "
            "though it is manageable with raised beds and good soil structure."
        )

    return CriterionResult(
        key=key,
        label="Water availability",
        status=status,  # type: ignore[arg-type]
        requirement=requirement,
        observed=f"{_fmt(actual, ' mm')} per year",
        explanation=explanation,
        weight=WEIGHTS[key],
        source=_requirement_source(plant),
    )


def _soil_match(plant: Plant, growing: GrowingInputs) -> CriterionResult:
    key = "soil_match"
    textures = [t.lower() for t in (plant.soil_textures or [])]
    requirement = (
        "A soil texture matching the plant's preference: " + ", ".join(textures)
        if textures
        else "Soil texture preference not recorded"
    )
    if not textures:
        return _unknown(key, "Soil suitability", requirement,
                        "This plant profile does not record a soil texture preference.")
    if not growing.soil_type:
        return _unknown(
            key,
            "Soil suitability",
            requirement,
            "No soil type was provided, so soil suitability was not assessed. "
            "Recording it would make the assessment more complete.",
        )

    chosen = growing.soil_type
    matched = any(chosen == texture or chosen in texture.split() for texture in textures)
    if matched:
        status = "pass"
        explanation = (
            f"The declared soil type ({chosen}) appears in this plant's preferred list."
        )
    elif any("loam" in texture for texture in textures) and chosen in {"sandy", "clay", "silt"}:
        status = "caution"
        explanation = (
            f"The declared soil type ({chosen}) is not in the preferred list, but this plant "
            "accepts loams and most soils can be moved towards a loam with organic matter."
        )
    else:
        status = "caution"
        explanation = (
            f"The declared soil type ({chosen}) does not match the recorded preference. "
            "Soil texture is modifiable with organic matter and drainage work."
        )
    return CriterionResult(
        key=key,
        label="Soil suitability",
        status=status,  # type: ignore[arg-type]
        requirement=requirement,
        observed=f"Declared soil type: {chosen}",
        explanation=explanation,
        weight=WEIGHTS[key],
        source=_requirement_source(plant),
    )


def _sunlight_match(plant: Plant, growing: GrowingInputs) -> CriterionResult:
    key = "sunlight_match"
    requirement_light = plant.sunlight_requirement
    requirement = (
        f"{SUNLIGHT_LABEL[requirement_light]}"
        + (f" ({_fmt(plant.sunlight_hours_min, ' h')} minimum)" if plant.sunlight_hours_min else "")
        if requirement_light
        else "Light requirement not recorded"
    )
    if requirement_light is None:
        return _unknown(key, "Light exposure", requirement,
                        "This plant profile does not record a light requirement.")
    if not growing.sunlight:
        return _unknown(
            key,
            "Light exposure",
            requirement,
            "No growing position was provided, so light exposure was not assessed.",
        )

    if requirement_light not in ORDINAL_SUNLIGHT:
        return _unknown(key, "Light exposure", requirement,
                        "The recorded light requirement could not be interpreted.")

    difference = abs(
        ORDINAL_SUNLIGHT.index(requirement_light) - ORDINAL_SUNLIGHT.index(growing.sunlight)
    )
    if difference == 0:
        status = "pass"
        explanation = "The declared position matches the recorded light requirement."
    elif difference == 1:
        status = "caution"
        explanation = (
            "The declared position is one step away from the recorded light requirement, "
            "which is usually workable but may reduce yield."
        )
    else:
        status = "fail"
        explanation = (
            "The declared position is at the opposite end of the light range from the "
            "recorded requirement."
        )
    return CriterionResult(
        key=key,
        label="Light exposure",
        status=status,  # type: ignore[arg-type]
        requirement=requirement,
        observed=SUNLIGHT_LABEL.get(growing.sunlight, growing.sunlight),
        explanation=explanation,
        weight=WEIGHTS[key],
        source=_requirement_source(plant),
    )


# ------------------------------------------------------------------ rollup


def _confidence(criteria: list[CriterionResult]) -> Confidence:
    total_weight = sum(item.weight for item in criteria)
    evaluated = [item for item in criteria if item.status != "unknown"]
    evaluated_weight = sum(item.weight for item in evaluated)
    value = round(evaluated_weight / total_weight, 3) if total_weight else 0.0
    if value >= 0.8:
        label = "high"
    elif value >= 0.55:
        label = "moderate"
    elif value > 0:
        label = "low"
    else:
        label = "none"
    return Confidence(
        value=value,
        label=label,  # type: ignore[arg-type]
        evaluated=len(evaluated),
        total=len(criteria),
        methodology=(
            "The confidence figure is the weighted share of applicable criteria that could "
            "be evaluated from recorded data. It measures evidence coverage and is not a "
            "probability that the crop will succeed."
        ),
    )


def _verdict(
    criteria: list[CriterionResult], climate: ClimateSnapshot
) -> tuple[str, str, str]:
    if not climate.available:
        return (
            "insufficient_data",
            "No climate baseline available for this location",
            climate.unavailable_reason
            or "Historical climate data could not be retrieved, so no climatological comparison was possible.",
        )

    evaluated = [item for item in criteria if item.status != "unknown"]
    if not evaluated:
        return (
            "insufficient_data",
            "Not enough recorded data to reach a verdict",
            "None of this plant's requirements could be compared against the local climate, "
            "so no assessment is offered rather than a misleading one.",
        )

    failures = [item for item in evaluated if item.status == "fail"]
    cautions = [item for item in evaluated if item.status == "caution"]

    if failures:
        names = ", ".join(item.label.lower() for item in failures)
        return (
            "not_supported",
            "The available conditions do not currently meet this plant's requirements",
            f"{len(failures)} of {len(evaluated)} evaluated criteria are not met ({names}). "
            "The detail below shows exactly which requirement falls short and by how much.",
        )
    if cautions:
        names = ", ".join(item.label.lower() for item in cautions)
        return (
            "potentially_suitable",
            "Growing looks possible, with limitations to manage",
            f"Every hard requirement is met, but {len(cautions)} of {len(evaluated)} evaluated "
            f"criteria need attention ({names}). With the adjustments suggested below this crop "
            "looks plausible here.",
        )
    return (
        "suitable",
        "Conditions match this plant's recorded requirements",
        f"All {len(evaluated)} evaluated criteria are met by the local climate and the inputs "
        "you provided. That is a good signal, though it is not a guarantee of a harvest.",
    )


def _limitations(plant: Plant, climate: ClimateSnapshot, growing: GrowingInputs) -> list[str]:
    items: list[str] = []
    if not climate.available:
        items.append(
            "No historical climate series could be retrieved for this location, so the verdict "
            "is 'insufficient data' rather than a judgement about the site."
        )
    else:
        items.append(
            f"Climate figures are climatological normals for {climate.baseline}, not a forecast. "
            "A single season can differ substantially from the long-term average."
        )
        items.append(
            "Climate values come from the reanalysis grid cell containing the coordinates. "
            "Local terrain, slope, frost pockets and coastal influence can change conditions "
            "within a short distance."
        )
        items.append(
            "Comparisons use monthly and annual aggregates. Short, severe events such as a "
            "single frost night or a heatwave are only partially represented."
        )
    items.append(
        "The plant requirement ranges are indicative agronomic envelopes compiled from "
        "published references. They are not cultivar-specific and should be validated locally."
    )
    if not growing.soil_type or not growing.sunlight or not growing.irrigation:
        missing = [
            name
            for name, value in (
                ("soil type", growing.soil_type),
                ("growing position", growing.sunlight),
                ("irrigation", growing.irrigation),
            )
            if not value
        ]
        items.append(
            "Not supplied, so not assessed: " + ", ".join(missing) + ". "
            "Providing these would raise the confidence of the assessment."
        )
    items.append(
        "Not modelled: soil chemistry beyond texture, drainage in practice, pests and diseases, "
        "variety choice, labour, input costs and market access."
    )
    items.append(
        "Documented cultivation regions elsewhere are evidence that the crop is grown there. "
        "They are not evidence that this location is suitable."
    )
    return items


def _next_steps(criteria: list[CriterionResult], plant: Plant) -> list[NextStep]:
    steps: list[NextStep] = []
    by_key = {item.key: item for item in criteria}

    cold = by_key.get("cold_temperature")
    if cold and cold.status in {"fail", "caution"}:
        steps.append(
            NextStep(
                title="Plan for cold",
                detail=(
                    "Choose cultivars bred for cooler conditions, use season extension such as "
                    "row cover or tunnels, and delay planting until the soil has warmed."
                ),
            )
        )
    heat = by_key.get("heat_temperature")
    if heat and heat.status in {"fail", "caution"}:
        steps.append(
            NextStep(
                title="Plan for heat",
                detail=(
                    "Shift the season to avoid the hottest weeks, use shade cloth or a shaded "
                    "position, and select heat-tolerant cultivars."
                ),
            )
        )
    frost = by_key.get("frost_risk")
    if frost and frost.status in {"fail", "caution"}:
        steps.append(
            NextStep(
                title="Manage frost risk",
                detail=(
                    "Track the local last-frost date, use frost covers or fleece, avoid low-lying "
                    "ground where cold air collects, and have protection ready for late frosts."
                ),
            )
        )
    water = by_key.get("water_balance")
    if water and water.status in {"fail", "caution"}:
        steps.append(
            NextStep(
                title="Secure a water plan",
                detail=(
                    "Measure how much water you can actually deliver, mulch to reduce evaporation, "
                    "and consider drip irrigation with a soil-moisture check before planting."
                ),
            )
        )
    window = by_key.get("growing_window")
    if window and window.status in {"fail", "caution"}:
        steps.append(
            NextStep(
                title="Match the cultivar to the season",
                detail=(
                    "Pick the shortest-season cultivar you can find, start it under protection, "
                    "and transplant as early as the conditions safely allow."
                ),
            )
        )
    soil = by_key.get("soil_match")
    if soil and soil.status == "caution":
        steps.append(
            NextStep(
                title="Improve the soil",
                detail=(
                    "Work in well-rotted organic matter, correct drainage where water stands, and "
                    "consider a raised bed to control the growing medium."
                ),
            )
        )
    sun = by_key.get("sunlight_match")
    if sun and sun.status in {"fail", "caution"}:
        steps.append(
            NextStep(
                title="Re-check the position",
                detail=(
                    "Track how many hours of direct sun the intended bed actually receives before "
                    "committing, and consider a different part of the site."
                ),
            )
        )
    if not steps:
        steps.append(
            NextStep(
                title="Start with a small trial",
                detail=(
                    "Conditions look favourable on paper. Plant a modest area first, keep notes on "
                    "dates and weather, and scale up from what you observe."
                ),
            )
        )
    steps.append(
        NextStep(
            title="Trial before you scale",
            detail=(
                "Grow a small test plot for one season and record establishment, growth and yield "
                "before committing land, water or money."
            ),
        )
    )
    return steps


# ------------------------------------------------------------------ entry


async def analyse_suitability(
    session: AsyncSession,
    plant: Plant,
    location: ResolvedLocation,
    growing: GrowingInputs,
    climate: ClimateSnapshot | None = None,
) -> SuitabilityResponse:
    if climate is None:
        climate = await get_climate_snapshot(session, location.latitude, location.longitude)

    criteria: list[CriterionResult] = [
        _cold_temperature(plant, climate),
        _heat_temperature(plant, climate),
        _frost_risk(plant, climate),
        _growing_window(plant, climate),
        _water_balance(plant, climate, growing),
        _soil_match(plant, growing),
        _sunlight_match(plant, growing),
    ]

    status, headline, summary = _verdict(criteria, climate)
    regions = [
        RegionSummary.model_validate(region, from_attributes=True)
        for region in (plant.regions or [])
    ]

    return SuitabilityResponse(
        plant=plant,  # type: ignore[arg-type]
        location=location,
        assessment=Assessment(
            status=status,  # type: ignore[arg-type]
            label=STATUS_LABEL[status],
            headline=headline,
            summary=summary,
            confidence=_confidence(criteria),
        ),
        climate=climate,
        criteria=criteria,
        limitations=_limitations(plant, climate, growing),
        next_steps=_next_steps(criteria, plant),
        cultivation_evidence=CultivationEvidence(
            available=bool(regions),
            regions=regions,
            note=(
                "These are places where cultivation of this crop is documented. They show that "
                "the crop is grown successfully somewhere with broadly comparable conditions; "
                "they are not an assessment of this location."
                if regions
                else "No documented cultivation regions are recorded for this crop yet."
            ),
        ),
        generated_explanation=None,
        methodology_version=METHODOLOGY_VERSION,
        evaluated_at=datetime.now(timezone.utc),
    )


def baseline_description() -> str:
    return (
        f"{settings.climate_baseline_label} daily reanalysis, aggregated to monthly and "
        "annual normals"
    )
