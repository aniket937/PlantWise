"""Climate provider: Open-Meteo historical weather archive (ERA5 reanalysis).

The service reduces a multi-year daily series into **climatological normals**
(monthly summaries plus annual aggregates). Aggregating over a ten-year baseline
is deliberate: a single weather observation says nothing about long-term
agricultural suitability, and the UI states this baseline explicitly.
"""

from __future__ import annotations

import logging
from calendar import month_name
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import UpstreamServiceError
from app.db.base import utcnow
from app.models import ClimateCache
from app.schemas.suitability import ClimateSnapshot, MonthClimate, MonthExtreme
from app.services.http_client import get_json

logger = logging.getLogger(__name__)

PROVIDER_NAME = "Open-Meteo historical weather archive (ERA5 reanalysis)"
SOURCE_URL = "https://open-meteo.com/en/docs/historical-weather-api"
COORDINATE_PRECISION = 2


def cache_key(latitude: float, longitude: float) -> str:
    return (
        f"{round(latitude, COORDINATE_PRECISION)}:"
        f"{round(longitude, COORDINATE_PRECISION)}:"
        f"{settings.climate_baseline_start_year}:{settings.climate_baseline_end_year}"
    )


def _fetch_window() -> tuple[date, date]:
    start = date(settings.climate_baseline_start_year, 1, 1)
    # ERA5 lags a few days behind real time; stop well clear of the archive edge.
    end = date(settings.climate_baseline_end_year, 12, 31)
    today = datetime.now(timezone.utc).date()
    if end > today - timedelta(days=10):
        end = today - timedelta(days=10)
    return start, end


def _clean(series: list[Any] | None) -> list[float | None]:
    if not series:
        return []
    cleaned: list[float | None] = []
    for value in series:
        if isinstance(value, (int, float)):
            cleaned.append(float(value))
        else:
            cleaned.append(None)
    return cleaned


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 2) if values else None


def summarise(daily: dict[str, Any], *, latitude: float, longitude: float,
              elevation: float | None, timezone_name: str | None) -> ClimateSnapshot:
    """Reduce Open-Meteo daily arrays into monthly and annual normals."""
    times = daily.get("time") or []
    tmax = _clean(daily.get("temperature_2m_max"))
    tmin = _clean(daily.get("temperature_2m_min"))
    precip = _clean(daily.get("precipitation_sum"))

    if not times or not tmax or not tmin:
        return ClimateSnapshot(
            available=False,
            source=PROVIDER_NAME,
            unavailable_reason="The climate provider returned no temperature series for this location.",
        )

    buckets: dict[int, dict[str, list[float]]] = {
        month: {"tmax": [], "tmin": [], "precip": []} for month in range(1, 13)
    }
    precip_years: dict[int, set[int]] = {month: set() for month in range(1, 13)}
    annual_precip: dict[int, float] = {}
    frost_days: dict[int, int] = {}
    gdd_by_year: dict[int, float] = {}
    all_tmax: list[float] = []
    all_tmin: list[float] = []

    for index, raw_day in enumerate(times):
        try:
            day = date.fromisoformat(str(raw_day))
        except ValueError:
            continue
        hi = tmax[index] if index < len(tmax) else None
        lo = tmin[index] if index < len(tmin) else None
        rain = precip[index] if index < len(precip) else None
        year = day.year

        if hi is not None:
            buckets[day.month]["tmax"].append(hi)
            all_tmax.append(hi)
        if lo is not None:
            buckets[day.month]["tmin"].append(lo)
            all_tmin.append(lo)
            if lo < 0.0:
                frost_days[year] = frost_days.get(year, 0) + 1
        if rain is not None:
            buckets[day.month]["precip"].append(rain)
            precip_years[day.month].add(year)
            annual_precip[year] = annual_precip.get(year, 0.0) + rain
        if hi is not None and lo is not None:
            gdd_by_year[year] = gdd_by_year.get(year, 0.0) + max(0.0, ((hi + lo) / 2.0) - 10.0)

    monthly: list[MonthClimate] = []
    for month in range(1, 13):
        bucket = buckets[month]
        month_tmin = _mean(bucket["tmin"]) or 0.0
        month_tmax = _mean(bucket["tmax"]) or 0.0
        total_rain = sum(bucket["precip"])
        years_with_data = max(1, len(precip_years[month]))
        monthly.append(
            MonthClimate(
                month=month_name[month],
                month_index=month,
                mean_min_c=month_tmin,
                mean_max_c=month_tmax,
                precipitation_mm=round(total_rain / years_with_data, 1),
            )
        )

    coldest = min(monthly, key=lambda item: item.mean_min_c)
    hottest = max(monthly, key=lambda item: item.mean_max_c)
    years = max(1, len(annual_precip))

    return ClimateSnapshot(
        available=True,
        source=PROVIDER_NAME,
        baseline=settings.climate_baseline_label,
        latitude=round(latitude, 4),
        longitude=round(longitude, 4),
        elevation_m=round(elevation, 1) if isinstance(elevation, (int, float)) else None,
        annual_mean_min_c=_mean(all_tmin),
        annual_mean_max_c=_mean(all_tmax),
        coldest_month=MonthExtreme(
            month=coldest.month, month_index=coldest.month_index, value_c=coldest.mean_min_c
        ),
        hottest_month=MonthExtreme(
            month=hottest.month, month_index=hottest.month_index, value_c=hottest.mean_max_c
        ),
        annual_precipitation_mm=round(sum(annual_precip.values()) / years, 1)
        if annual_precip
        else None,
        frost_days_per_year=int(round(sum(frost_days.values()) / years)) if frost_days else 0,
        growing_degree_days_base10=round(sum(gdd_by_year.values()) / max(1, len(gdd_by_year)))
        if gdd_by_year
        else None,
        monthly=monthly,
    )


async def _load_cached(session: AsyncSession, key: str) -> ClimateCache | None:
    result = await session.execute(
        select(ClimateCache).where(ClimateCache.cache_key == key)
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        return None
    fetched = entry.fetched_at
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=timezone.utc)
    age = utcnow() - fetched
    if age > timedelta(hours=settings.climate_cache_ttl_hours):
        return None
    return entry


async def _store_cache(
    session: AsyncSession, key: str, latitude: float, longitude: float, snapshot: ClimateSnapshot
) -> None:
    existing = await _load_cached(session, key)
    payload = snapshot.model_dump(mode="json")
    if existing is not None:
        existing.payload = payload
        existing.fetched_at = utcnow()
    else:
        session.add(
            ClimateCache(
                cache_key=key,
                latitude=round(latitude, COORDINATE_PRECISION),
                longitude=round(longitude, COORDINATE_PRECISION),
                source=PROVIDER_NAME,
                fetched_at=utcnow(),
                payload=payload,
            )
        )
    try:
        await session.commit()
    except Exception:  # pragma: no cover - cache writes must never break a request
        await session.rollback()
        logger.warning("Could not persist climate cache entry for %s", key, exc_info=True)


async def get_climate_snapshot(
    session: AsyncSession, latitude: float, longitude: float
) -> ClimateSnapshot:
    """Return climatological normals, preferring a fresh cached copy."""
    key = cache_key(latitude, longitude)
    cached = await _load_cached(session, key)
    if cached is not None:
        try:
            return ClimateSnapshot.model_validate(cached.payload)
        except Exception:  # pragma: no cover - stale/incompatible cache payload
            logger.warning("Discarding unreadable climate cache entry %s", key)

    start, end = _fetch_window()
    try:
        payload = await get_json(
            settings.open_meteo_archive_url,
            params={
                "latitude": round(latitude, 4),
                "longitude": round(longitude, 4),
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "auto",
                "temperature_unit": "celsius",
                "precipitation_unit": "mm",
            },
            provider="Open-Meteo archive",
        )
    except UpstreamServiceError as exc:
        return ClimateSnapshot(
            available=False,
            source=PROVIDER_NAME,
            baseline=settings.climate_baseline_label,
            latitude=round(latitude, 4),
            longitude=round(longitude, 4),
            unavailable_reason=(
                "Historical climate data could not be retrieved for this location "
                f"({exc.details.get('reason') if exc.details else 'unavailable'})."
            ),
        )

    snapshot = summarise(
        payload.get("daily") or {},
        latitude=latitude,
        longitude=longitude,
        elevation=payload.get("elevation"),
        timezone_name=payload.get("timezone"),
    )
    if snapshot.available:
        await _store_cache(session, key, latitude, longitude, snapshot)
    return snapshot
