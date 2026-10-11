"""Documented cultivation regions: list them and derive map presentation.

The map is a *secondary* view. Every marker is accompanied by the structured
region list in the API response, so the UI always has a non-map representation
of the same information.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Plant
from app.schemas.regions import (
    MapMarker,
    PlantRegionsResponse,
    RegionMapConfig,
    RegionPlantListResponse,
    RegionPlantOption,
)
from app.services.plants import to_region_summary, to_summary

OSM_TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
OSM_ATTRIBUTION = "OpenStreetMap contributors"
MAP_DETAIL = (
    "Markers show documented cultivation areas from the plant profile. Base map tiles come "
    "from OpenStreetMap. The list below contains the same regions and is the authoritative view."
)
DOCUMENTED_NOTE = (
    "Documented cultivation means production of this crop is recorded in that place. It is "
    "evidence about that region, not a prediction for the coordinates you are viewing."
)


def _map_config(regions: list) -> RegionMapConfig:
    if regions:
        center_lat = sum(r.latitude for r in regions) / len(regions)
        center_lon = sum(r.longitude for r in regions) / len(regions)
        spread = max(
            max(r.latitude for r in regions) - min(r.latitude for r in regions),
            max(r.longitude for r in regions) - min(r.longitude for r in regions),
        )
        zoom = 2 if spread > 60 else 3 if spread > 25 else 4
    else:
        center_lat, center_lon, zoom = 20.0, 0.0, 2
    return RegionMapConfig(
        available=True,
        tile_url=OSM_TILE_URL,
        attribution=OSM_ATTRIBUTION,
        default_center=(round(center_lat, 3), round(center_lon, 3)),
        default_zoom=zoom,
        detail=MAP_DETAIL,
    )


async def plant_region_options(session: AsyncSession) -> RegionPlantListResponse:
    plants = list((await session.execute(select(Plant))).scalars().unique().all())
    options = [
        RegionPlantOption(
            slug=plant.slug,
            common_name=plant.common_name,
            scientific_name=plant.scientific_name,
            image_url=plant.image_url,
            region_count=len(plant.regions or []),
        )
        for plant in plants
        if plant.regions
    ]
    options.sort(key=lambda option: (-option.region_count, option.common_name))
    return RegionPlantListResponse(items=options)


def build_plant_regions(plant: Plant) -> PlantRegionsResponse:
    regions = list(plant.regions or [])
    markers = [
        MapMarker(
            slug=region.slug,
            name=region.name,
            country=region.country,
            latitude=region.latitude,
            longitude=region.longitude,
            evidence_type=region.evidence_type,
        )
        for region in regions
    ]
    notes = [DOCUMENTED_NOTE]
    if any(region.evidence_type == "inferred_suitability" for region in regions):
        notes.append(
            "Some entries are modelled inferences rather than documented production; each item "
            "states which it is, and the two are never blended into one map layer."
        )
    if not regions:
        notes.append("No cultivation regions are recorded for this plant yet.")
    return PlantRegionsResponse(
        plant=to_summary(plant),
        regions=[to_region_summary(region) for region in regions],
        markers=markers,
        map=_map_config(regions),
        notes=notes,
        generated_at=datetime.now(timezone.utc),
    )
