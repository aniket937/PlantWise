"""ORM models.

The schema is deliberately small: structured plant profiles, the documented
cultivation regions attached to them, a cache for climate lookups, and a light
search log used for the "popular / recently searched" surfaces.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Plant(TimestampMixin, Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identity -----------------------------------------------------------
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    common_name: Mapped[str] = mapped_column(String(120), index=True)
    scientific_name: Mapped[str] = mapped_column(String(160), index=True)
    family: Mapped[str | None] = mapped_column(String(120), default=None)
    short_description: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text, default=None)

    # Imagery ------------------------------------------------------------
    image_url: Mapped[str | None] = mapped_column(String(512), default=None)
    image_attribution: Mapped[str | None] = mapped_column(String(255), default=None)
    image_license: Mapped[str | None] = mapped_column(String(120), default=None)
    image_source_url: Mapped[str | None] = mapped_column(String(512), default=None)

    # Classification -----------------------------------------------------
    lifecycle: Mapped[str | None] = mapped_column(String(40), default=None)
    growth_habit: Mapped[str | None] = mapped_column(String(60), default=None)
    difficulty: Mapped[str | None] = mapped_column(String(40), default=None)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Temperature --------------------------------------------------------
    temp_min_c: Mapped[float | None] = mapped_column(Float, default=None)
    temp_max_c: Mapped[float | None] = mapped_column(Float, default=None)
    temp_optimal_min_c: Mapped[float | None] = mapped_column(Float, default=None)
    temp_optimal_max_c: Mapped[float | None] = mapped_column(Float, default=None)
    temperature_notes: Mapped[str | None] = mapped_column(Text, default=None)
    frost_tolerance: Mapped[str | None] = mapped_column(String(40), default=None)

    # Rainfall -----------------------------------------------------------
    rainfall_min_mm: Mapped[float | None] = mapped_column(Float, default=None)
    rainfall_max_mm: Mapped[float | None] = mapped_column(Float, default=None)
    rainfall_notes: Mapped[str | None] = mapped_column(Text, default=None)

    # Soil ---------------------------------------------------------------
    soil_ph_min: Mapped[float | None] = mapped_column(Float, default=None)
    soil_ph_max: Mapped[float | None] = mapped_column(Float, default=None)
    soil_textures: Mapped[list[str]] = mapped_column(JSON, default=list)
    soil_drainage: Mapped[str | None] = mapped_column(String(60), default=None)
    soil_notes: Mapped[str | None] = mapped_column(Text, default=None)

    # Water / sunlight ---------------------------------------------------
    water_requirement: Mapped[str | None] = mapped_column(String(40), default=None)
    water_notes: Mapped[str | None] = mapped_column(Text, default=None)
    sunlight_requirement: Mapped[str | None] = mapped_column(String(40), default=None)
    sunlight_hours_min: Mapped[float | None] = mapped_column(Float, default=None)
    sunlight_notes: Mapped[str | None] = mapped_column(Text, default=None)

    # Season -------------------------------------------------------------
    growing_season_days_min: Mapped[int | None] = mapped_column(Integer, default=None)
    growing_season_days_max: Mapped[int | None] = mapped_column(Integer, default=None)
    growing_season_notes: Mapped[str | None] = mapped_column(Text, default=None)

    # Structured supporting content --------------------------------------
    cultivation_steps: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    common_problems: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    data_sources: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)

    # Popularity ---------------------------------------------------------
    search_count: Mapped[int] = mapped_column(Integer, default=0)

    regions: Mapped[list["CultivationRegion"]] = relationship(
        back_populates="plant",
        cascade="all, delete-orphan",
        order_by="CultivationRegion.rank",
        lazy="selectin",
    )

    @property
    def display_name(self) -> str:
        return f"{self.common_name} ({self.scientific_name})"


class CultivationRegion(TimestampMixin, Base):
    """A place where cultivation of a plant is *documented*, plus provenance."""

    __tablename__ = "cultivation_regions"

    id: Mapped[int] = mapped_column(primary_key=True)
    plant_id: Mapped[int] = mapped_column(
        ForeignKey("plants.id", ondelete="CASCADE"), index=True
    )

    slug: Mapped[str] = mapped_column(String(120), index=True)
    name: Mapped[str] = mapped_column(String(160))
    country: Mapped[str] = mapped_column(String(120))
    country_code: Mapped[str | None] = mapped_column(String(3), default=None)
    admin_area: Mapped[str | None] = mapped_column(String(160), default=None)

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    # "documented_cultivation" (a real production area) or
    # "inferred_suitability" (modelled, must never be presented as a farm).
    evidence_type: Mapped[str] = mapped_column(
        String(40), default="documented_cultivation"
    )
    description: Mapped[str | None] = mapped_column(Text, default=None)
    climate_note: Mapped[str | None] = mapped_column(Text, default=None)
    rank: Mapped[int] = mapped_column(Integer, default=100)
    data_sources: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)

    plant: Mapped[Plant] = relationship(back_populates="regions", lazy="raise")


class ClimateCache(TimestampMixin, Base):
    """Climatology snapshots keyed by rounded coordinates + baseline window."""

    __tablename__ = "climate_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(80))
    fetched_at: Mapped[datetime] = mapped_column()
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class SearchQuery(TimestampMixin, Base):
    """Lightweight log powering "recently searched" without any user account."""

    __tablename__ = "search_queries"

    id: Mapped[int] = mapped_column(primary_key=True)
    query: Mapped[str] = mapped_column(String(200), index=True)
    plant_id: Mapped[int | None] = mapped_column(
        ForeignKey("plants.id", ondelete="SET NULL"), default=None
    )
    matched: Mapped[bool] = mapped_column(default=False)
