"""Idempotent database seeding.

Running this repeatedly is safe: plants are matched on slug and updated in
place, so a corrected figure in the seed data propagates on the next start
without duplicating rows. ``search_count`` is deliberately preserved because it
is accumulated runtime data, not seed content.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CultivationRegion, Plant
from app.services.seed_data import all_seed_plants

logger = logging.getLogger(__name__)

IDENTITY_FIELDS = {"slug"}
PROTECTED_FIELDS = {"id", "regions", "search_count", "created_at", "updated_at"}


@dataclass(slots=True)
class SeedResult:
    inserted: int = 0
    updated: int = 0
    regions: int = 0

    @property
    def total(self) -> int:
        return self.inserted + self.updated


def _scalar_fields(profile: dict) -> dict:
    return {key: value for key, value in profile.items() if key not in PROTECTED_FIELDS}


def _region_rows(plant: Plant, profile: dict) -> list[CultivationRegion]:
    rows: list[CultivationRegion] = []
    for entry in profile.get("regions") or []:
        if not isinstance(entry, dict):
            continue
        rows.append(
            CultivationRegion(
                slug=str(entry.get("slug", "")).strip(),
                name=str(entry.get("name", "")).strip(),
                country=str(entry.get("country", "")).strip(),
                country_code=entry.get("country_code"),
                admin_area=entry.get("admin_area"),
                latitude=float(entry["latitude"]),
                longitude=float(entry["longitude"]),
                evidence_type=str(entry.get("evidence_type", "documented_cultivation")),
                description=entry.get("description"),
                climate_note=entry.get("climate_note"),
                rank=int(entry.get("rank", 100)),
                data_sources=list(entry.get("data_sources") or []),
            )
        )
    return rows


async def seed_database(session: AsyncSession, *, force: bool = False) -> SeedResult:
    result = SeedResult()
    profiles = all_seed_plants()

    existing_rows = list((await session.execute(select(Plant))).scalars().unique().all())
    existing_by_slug = {plant.slug: plant for plant in existing_rows}

    for profile in profiles:
        slug = profile["slug"]
        plant = existing_by_slug.get(slug)

        if plant is None:
            plant = Plant(**_scalar_fields(profile))
            plant.regions = _region_rows(plant, profile)
            session.add(plant)
            existing_by_slug[slug] = plant
            result.inserted += 1
            result.regions += len(plant.regions)
            continue

        if not force:
            changed = False
            for key, value in _scalar_fields(profile).items():
                if getattr(plant, key) != value:
                    setattr(plant, key, value)
                    changed = True
            if changed:
                result.updated += 1
            continue

        for key, value in _scalar_fields(profile).items():
            setattr(plant, key, value)
        plant.regions.clear()
        plant.regions.extend(_region_rows(plant, profile))
        result.updated += 1
        result.regions += len(plant.regions)

    await session.flush()
    logger.info(
        "Seeded plants: %d inserted, %d updated, %d regions",
        result.inserted,
        result.updated,
        result.regions,
    )
    return result


async def plant_count(session: AsyncSession) -> int:
    return int((await session.execute(select(func.count()).select_from(Plant))).scalar_one())
