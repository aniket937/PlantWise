"""Plant browsing endpoints."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ResourceNotFoundError
from app.db.session import get_session
from app.schemas.plant import (
    PlantCollection,
    PlantDetail,
    PlantListResponse,
)
from app.services import plants as plant_service

router = APIRouter(prefix="/plants", tags=["plants"])

LifecycleFilter = Literal["annual", "biennial", "perennial"]
DifficultyFilter = Literal["beginner", "intermediate", "advanced"]


@router.get("", response_model=PlantListResponse, summary="Search and filter plant profiles")
async def list_plants(
    session: AsyncSession = Depends(get_session),
    query: str | None = Query(default=None, max_length=120, description="Free-text search"),
    lifecycle: LifecycleFilter | None = Query(default=None),
    difficulty: DifficultyFilter | None = Query(default=None),
    tag: str | None = Query(default=None, max_length=40),
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=2000),
) -> PlantListResponse:
    found, total = await plant_service.list_plants(
        session,
        query=query,
        lifecycle=lifecycle,
        difficulty=difficulty,
        tag=tag,
        limit=limit,
        offset=offset,
    )

    suggestions: list[str] = []
    if query and not found:
        suggestions = await plant_service.suggestions(session, query)
    if query:
        await plant_service.record_search(session, query, found[0] if found else None, bool(found))
        await session.commit()

    return PlantListResponse(
        items=[plant_service.to_summary(plant) for plant in found],
        total=total,
        query=query,
        suggestions=suggestions,
    )


@router.get(
    "/featured",
    response_model=PlantCollection,
    summary="Curated home-page collections",
)
async def featured(session: AsyncSession = Depends(get_session)) -> PlantCollection:
    popular = await plant_service.popular_plants(session, limit=6)
    recent = await plant_service.recently_viewed(session, limit=6)
    total = await plant_service.count_plants(session)
    return PlantCollection(
        popular=[plant_service.to_summary(plant) for plant in popular],
        recent=[plant_service.to_summary(plant) for plant in recent],
        total=total,
    )


@router.get("/{slug}", response_model=PlantDetail, summary="Full profile for one plant")
async def get_plant(slug: str, session: AsyncSession = Depends(get_session)) -> PlantDetail:
    plant = await plant_service.get_by_slug(session, slug)
    if plant is None:
        raise ResourceNotFoundError(
            f"No plant profile matches '{slug}'.", code="plant_not_found"
        )
    await plant_service.bump_popularity(session, plant)
    await session.commit()
    return plant_service.to_detail(plant)
