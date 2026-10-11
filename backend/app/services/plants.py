"""Plant repository and ORM-to-schema serialisers.

All queries use the 2.0 style ``select()`` API and eager-load the documented
cultivation regions, so no lazy load can fire outside an active session.
"""

from __future__ import annotations

import difflib

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Plant, SearchQuery
from app.schemas.common import DataSource
from app.schemas.plant import (
    CommonProblem,
    CultivationStep,
    GrowingSeason,
    PlantDetail,
    PlantSummary,
    RainfallProfile,
    RegionSummary,
    SoilProfile,
    SunlightProfile,
    TemperatureProfile,
    WaterProfile,
)


def _sources(raw: object) -> list[DataSource]:
    if not isinstance(raw, list):
        return []
    out: list[DataSource] = []
    for entry in raw:
        if isinstance(entry, dict) and entry.get("label"):
            out.append(DataSource.model_validate(entry))
    return out


def _first_source(raw: object) -> DataSource | None:
    sources = _sources(raw)
    return sources[0] if sources else None


def to_region_summary(region: object) -> RegionSummary:
    return RegionSummary.model_validate(region, from_attributes=True)


def to_summary(plant: Plant) -> PlantSummary:
    return PlantSummary(
        slug=plant.slug,
        common_name=plant.common_name,
        scientific_name=plant.scientific_name,
        family=plant.family,
        short_description=plant.short_description,
        image_url=plant.image_url,
        image_attribution=plant.image_attribution,
        image_license=plant.image_license,
        image_source_url=plant.image_source_url,
        lifecycle=plant.lifecycle,  # type: ignore[arg-type]
        growth_habit=plant.growth_habit,
        difficulty=plant.difficulty,  # type: ignore[arg-type]
        tags=list(plant.tags or []),
        data_sources=_sources(plant.data_sources),
    )


def to_detail(plant: Plant) -> PlantDetail:
    summary = to_summary(plant)
    primary = _first_source(plant.data_sources)

    temperature = TemperatureProfile(
        min_c=plant.temp_min_c,
        max_c=plant.temp_max_c,
        optimal_min_c=plant.temp_optimal_min_c,
        optimal_max_c=plant.temp_optimal_max_c,
        frost_tolerance=plant.frost_tolerance,  # type: ignore[arg-type]
        notes=plant.temperature_notes,
        source=primary,
    )
    rainfall = RainfallProfile(
        min_mm=plant.rainfall_min_mm,
        max_mm=plant.rainfall_max_mm,
        notes=plant.rainfall_notes,
        source=primary,
    )
    soil = SoilProfile(
        textures=list(plant.soil_textures or []),
        ph_min=plant.soil_ph_min,
        ph_max=plant.soil_ph_max,
        drainage=plant.soil_drainage,
        notes=plant.soil_notes,
        source=primary,
    )
    water = WaterProfile(
        requirement=plant.water_requirement,  # type: ignore[arg-type]
        notes=plant.water_notes,
        source=primary,
    )
    sunlight = SunlightProfile(
        requirement=plant.sunlight_requirement,  # type: ignore[arg-type]
        hours_min=plant.sunlight_hours_min,
        notes=plant.sunlight_notes,
        source=primary,
    )
    season = GrowingSeason(
        days_min=plant.growing_season_days_min,
        days_max=plant.growing_season_days_max,
        notes=plant.growing_season_notes,
    )

    steps = [
        CultivationStep.model_validate(entry)
        for entry in (plant.cultivation_steps or [])
        if isinstance(entry, dict)
    ]
    problems = [
        CommonProblem.model_validate(entry)
        for entry in (plant.common_problems or [])
        if isinstance(entry, dict)
    ]

    return PlantDetail(
        **summary.model_dump(),
        description=plant.description,
        temperature=temperature,
        rainfall=rainfall,
        soil=soil,
        water=water,
        sunlight=sunlight,
        growing_season=season,
        cultivation_steps=sorted(steps, key=lambda step: step.order),
        common_problems=problems,
        regions=[to_region_summary(region) for region in (plant.regions or [])],
        popularity=plant.search_count or 0,
    )


def _search_filter(term: str):
    pattern = f"%{term.lower()}%"
    return or_(
        func.lower(Plant.common_name).like(pattern),
        func.lower(Plant.scientific_name).like(pattern),
        func.lower(func.coalesce(Plant.family, "")).like(pattern),
        func.lower(Plant.short_description).like(pattern),
        func.lower(func.coalesce(Plant.description, "")).like(pattern),
        func.lower(cast(Plant.tags, String)).like(pattern),
    )


async def list_plants(
    session: AsyncSession,
    query: str | None = None,
    lifecycle: str | None = None,
    difficulty: str | None = None,
    tag: str | None = None,
    limit: int = 24,
    offset: int = 0,
) -> tuple[list[Plant], int]:
    statement = select(Plant)
    if query:
        statement = statement.where(_search_filter(query.strip()))
    if lifecycle:
        statement = statement.where(Plant.lifecycle == lifecycle)
    if difficulty:
        statement = statement.where(Plant.difficulty == difficulty)
    if tag:
        statement = statement.where(
            func.lower(cast(Plant.tags, String)).like(f"%{tag.strip().lower()}%")
        )

    count_statement = select(func.count()).select_from(statement.subquery())
    total = int((await session.execute(count_statement)).scalar_one())

    statement = statement.order_by(Plant.common_name.asc()).limit(limit).offset(offset)
    plants = list((await session.execute(statement)).scalars().unique().all())
    return plants, total


async def get_by_slug(session: AsyncSession, slug: str) -> Plant | None:
    statement = select(Plant).where(Plant.slug == slug)
    return (await session.execute(statement)).scalars().first()


async def get_by_id(session: AsyncSession, plant_id: int) -> Plant | None:
    statement = select(Plant).where(Plant.id == plant_id)
    return (await session.execute(statement)).scalars().first()


async def popular_plants(session: AsyncSession, limit: int = 6) -> list[Plant]:
    statement = (
        select(Plant)
        .where(Plant.search_count > 0)
        .order_by(Plant.search_count.desc(), Plant.common_name.asc())
        .limit(limit)
    )
    return list((await session.execute(statement)).scalars().unique().all())


async def recently_viewed(session: AsyncSession, limit: int = 6) -> list[Plant]:
    statement = (
        select(SearchQuery.query)
        .where(SearchQuery.matched.is_(True))
        .order_by(SearchQuery.created_at.desc())
        .limit(limit * 3)
    )
    slugs = [row for row in (await session.execute(statement)).scalars().all() if row]
    ordered: list[str] = []
    for slug in slugs:
        if slug not in ordered:
            ordered.append(slug)
        if len(ordered) >= limit:
            break
    if not ordered:
        return []
    plants = list(
        (await session.execute(select(Plant).where(Plant.slug.in_(ordered)))).scalars().unique().all()
    )
    by_slug = {plant.slug: plant for plant in plants}
    return [by_slug[slug] for slug in ordered if slug in by_slug]


async def record_search(
    session: AsyncSession, query: str, plant: Plant | None, matched: bool
) -> None:
    cleaned = query.strip()[:200]
    if not cleaned:
        return
    session.add(
        SearchQuery(query=cleaned, plant_id=plant.id if plant else None, matched=matched)
    )
    await session.flush()


async def bump_popularity(session: AsyncSession, plant: Plant) -> None:
    plant.search_count = (plant.search_count or 0) + 1
    await session.flush()


async def suggestions(session: AsyncSession, query: str, limit: int = 5) -> list[str]:
    """Close matches offered when a search returns nothing."""
    rows = (
        await session.execute(select(Plant.common_name, Plant.slug))
    ).all()
    haystack = [f"{name}" for name, _ in rows]
    pool = [f"{name} ({slug})" for name, slug in rows]
    matches = difflib.get_close_matches(query.strip(), haystack, n=limit, cutoff=0.4)
    if not matches:
        matches = [
            name for name in haystack if query.strip().lower()[:3] in name.lower()
        ][:limit]
    return [pool[haystack.index(name)] for name in matches]


async def count_plants(session: AsyncSession) -> int:
    return int((await session.execute(select(func.count()).select_from(Plant))).scalar_one())
