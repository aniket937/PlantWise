"""Deterministic tests for the suitability engine.

No network anywhere: climate snapshots are hand-built and passed straight into
``analyse_suitability``, and plants live in an in-memory database. Assertions run
on fully materialised pydantic responses, outside the event loop.
"""

from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.models import Plant
from app.schemas.suitability import (
    ClimateSnapshot,
    GrowingInputs,
    MonthClimate,
    MonthExtreme,
    ResolvedLocation,
    SuitabilityResponse,
)
from app.services.suitability import analyse_suitability

from tests.conftest import run_on, session

TOMATO = {
    "slug": "tomato",
    "common_name": "Tomato",
    "scientific_name": "Solanum lycopersicum",
    "short_description": "A widely grown warm-season crop.",
    "temp_min_c": 10.0,
    "temp_max_c": 30.0,
    "frost_tolerance": "none",
    "rainfall_min_mm": 400.0,
    "rainfall_max_mm": 1000.0,
    "soil_textures": ["loam"],
    "sunlight_requirement": "full_sun",
    "growing_season_days_min": 80,
    "data_sources": [{"label": "Test reference", "url": "https://example.org", "note": None}],
}

LOCATION = ResolvedLocation(
    label="Test site",
    latitude=-1.28,
    longitude=36.82,
    source="test",
)


def _months(mean_min: float, clamp: bool = True) -> list[MonthClimate]:
    floor = max(mean_min, 10) if clamp else mean_min
    return [
        MonthClimate(
            month="January",
            month_index=1,
            mean_min_c=mean_min,
            mean_max_c=mean_min + 12,
            precipitation_mm=80.0,
        ),
        *[
            MonthClimate(
                month=f"M{index}",
                month_index=index,
                mean_min_c=floor,
                mean_max_c=floor + 12,
                precipitation_mm=80.0,
            )
            for index in range(2, 13)
        ],
    ]


def warm_climate() -> ClimateSnapshot:
    return ClimateSnapshot(
        available=True,
        source="test",
        baseline="test",
        coldest_month=MonthExtreme(month="January", month_index=1, value_c=14.0),
        hottest_month=MonthExtreme(month="March", month_index=3, value_c=28.0),
        annual_precipitation_mm=950.0,
        frost_days_per_year=0,
        monthly=_months(14.0),
    )


def cold_climate() -> ClimateSnapshot:
    return ClimateSnapshot(
        available=True,
        source="test",
        baseline="test",
        coldest_month=MonthExtreme(month="January", month_index=1, value_c=-6.0),
        hottest_month=MonthExtreme(month="July", month_index=7, value_c=16.0),
        annual_precipitation_mm=700.0,
        frost_days_per_year=120,
        monthly=_months(-6.0),
    )


def polar_climate() -> ClimateSnapshot:
    return ClimateSnapshot(
        available=True,
        source="test",
        baseline="test",
        coldest_month=MonthExtreme(month="January", month_index=1, value_c=-18.0),
        hottest_month=MonthExtreme(month="July", month_index=7, value_c=6.0),
        annual_precipitation_mm=300.0,
        frost_days_per_year=300,
        monthly=_months(-18.0, clamp=False),
    )


def dry_climate() -> ClimateSnapshot:
    return ClimateSnapshot(
        available=True,
        source="test",
        baseline="test",
        coldest_month=MonthExtreme(month="January", month_index=1, value_c=12.0),
        hottest_month=MonthExtreme(month="March", month_index=3, value_c=31.0),
        annual_precipitation_mm=150.0,
        frost_days_per_year=1,
        monthly=_months(12.0),
    )


def unavailable_climate() -> ClimateSnapshot:
    return ClimateSnapshot(
        available=False,
        source="test",
        baseline="test",
        unavailable_reason="Test has no data on purpose.",
    )


def _assess(
    engine: AsyncEngine,
    loop: asyncio.AbstractEventLoop,
    climate: ClimateSnapshot,
    growing: GrowingInputs | None = None,
) -> SuitabilityResponse:
    async def run() -> SuitabilityResponse:
        async with await session(engine) as db_session:
            plant = Plant(**TOMATO)
            plant.regions = []
            db_session.add(plant)
            await db_session.flush()
            return await analyse_suitability(
                db_session,
                plant,
                LOCATION,
                growing or GrowingInputs(),
                climate=climate,
            )

    return run_on(loop, run())


def _by_key(result: SuitabilityResponse, key: str) -> Any:
    for criterion in result.criteria:
        if criterion.key == key:
            return criterion
    raise AssertionError(f"criterion {key} missing from {[c.key for c in result.criteria]}")


def test_full_inputs_warm_site_is_suitable(db):
    engine, loop = db
    result = _assess(
        engine,
        loop,
        warm_climate(),
        GrowingInputs(soil_type="loam", sunlight="full_sun", irrigation="regular"),
    )
    assert result.assessment.status == "suitable"
    assert result.assessment.confidence.label == "high"
    assert result.assessment.confidence.evaluated == 7
    assert all(criterion.status == "pass" for criterion in result.criteria)


def test_cold_site_rejects_a_sensitive_crop(db):
    engine, loop = db
    result = _assess(engine, loop, cold_climate())
    assert result.assessment.status == "not_supported"
    assert _by_key(result, "cold_temperature").status == "fail"
    assert _by_key(result, "frost_risk").status == "fail"
    # The growing window can still pass: months 2-12 clamp to 10 C here, so even
    # a season-long cold spell is not what drives the rejection.


def test_short_growing_window_fails(db):
    engine, loop = db
    result = _assess(engine, loop, polar_climate())
    assert _by_key(result, "growing_window").status == "fail"
    assert _by_key(result, "growing_window").observed.startswith("0 of 12")


def test_marginal_cold_is_caution_not_fail(db):
    engine, loop = db
    climate = warm_climate()
    climate.coldest_month = MonthExtreme(month="January", month_index=1, value_c=9.0)
    result = _assess(engine, loop, climate)
    assert _by_key(result, "cold_temperature").status == "caution"


def test_declared_irrigation_closes_a_water_gap(db):
    engine, loop = db
    result = _assess(
        engine,
        loop,
        dry_climate(),
        GrowingInputs(irrigation="regular", soil_type="loam", sunlight="full_sun"),
    )
    assert _by_key(result, "water_balance").status == "pass"
    assert "irrigation" in _by_key(result, "water_balance").explanation.lower()


def test_missing_inputs_are_reported_unknown_not_guessed(db):
    engine, loop = db
    result = _assess(engine, loop, warm_climate())
    assert _by_key(result, "soil_match").status == "unknown"
    assert _by_key(result, "sunlight_match").status == "unknown"
    assert "Not supplied, so not assessed" in " ".join(result.limitations)
    assert result.assessment.confidence.evaluated == 5


def test_no_climate_means_insufficient_data(db):
    engine, loop = db
    result = _assess(engine, loop, unavailable_climate())
    assert result.assessment.status == "insufficient_data"
    assert result.assessment.confidence.value == 0.0
    assert any("No historical climate series" in item for item in result.limitations)


def test_verdict_never_claims_a_percentage(db):
    engine, loop = db
    result = _assess(engine, loop, warm_climate())
    for text in (result.assessment.summary, result.assessment.headline):
        assert "%" not in text
    for criterion in result.criteria:
        assert "%" not in criterion.explanation


def test_heat_exceeding_tolerance_marks_not_supported(db):
    engine, loop = db
    climate = warm_climate()
    climate.hottest_month = MonthExtreme(month="March", month_index=3, value_c=36.0)
    result = _assess(engine, loop, climate)
    assert _by_key(result, "heat_temperature").status == "fail"
    assert result.assessment.status == "not_supported"