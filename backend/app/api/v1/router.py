"""Aggregate v1 router."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import assistant, health, locations, plants, regions, suitability

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(plants.router)
api_router.include_router(locations.router)
api_router.include_router(suitability.router)
api_router.include_router(regions.router)
api_router.include_router(assistant.router)

__all__ = ["api_router"]
