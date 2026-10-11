"""Documented cultivation regions per plant."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ResourceNotFoundError
from app.db.session import get_session
from app.schemas.regions import PlantRegionsResponse, RegionPlantListResponse
from app.services.plants import get_by_slug
from app.services.regions import build_plant_regions, plant_region_options

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get(
    "/plants",
    response_model=RegionPlantListResponse,
    summary="Plants that have documented cultivation regions",
)
async def plants_with_regions(
    session: AsyncSession = Depends(get_session),
) -> RegionPlantListResponse:
    return await plant_region_options(session)


@router.get(
    "/{plant_slug}",
    response_model=PlantRegionsResponse,
    summary="Map and list of documented cultivation regions for a plant",
)
async def regions_for_plant(
    plant_slug: str, session: AsyncSession = Depends(get_session)
) -> PlantRegionsResponse:
    plant = await get_by_slug(session, plant_slug)
    if plant is None:
        raise ResourceNotFoundError(
            f"No plant profile matches '{plant_slug}'.", code="plant_not_found"
        )
    return build_plant_regions(plant)
