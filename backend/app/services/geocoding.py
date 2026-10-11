"""Geocoding providers.

Two interchangeable implementations sit behind one interface and are selected by
``GEOCODING_PROVIDER``. The default is Open-Meteo's geocoder because it shares
the climate provider's API surface and licensing; Nominatim is available for
deployments that prefer OpenStreetMap data and accept its usage policy
(identifying User-Agent, no bulk querying, caching of results).
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from app.core.config import settings
from app.core.errors import UpstreamServiceError
from app.schemas.location import GeocodedLocation
from app.services.http_client import get_json

logger = logging.getLogger(__name__)


class GeocodingProvider(Protocol):
    name: str

    async def search(self, query: str, *, limit: int = 6) -> list[GeocodedLocation]: ...


def _label(*parts: str | None) -> str:
    seen: list[str] = []
    for part in parts:
        cleaned = (part or "").strip()
        if cleaned and cleaned not in seen:
            seen.append(cleaned)
    return ", ".join(seen)


class OpenMeteoGeocoding:
    name = "open-meteo"

    async def search(self, query: str, *, limit: int = 6) -> list[GeocodedLocation]:
        payload = await get_json(
            settings.open_meteo_geocoding_url,
            params={
                "name": query,
                "count": min(max(limit, 1), 20),
                "language": "en",
                "format": "json",
            },
            provider="Open-Meteo geocoding",
        )
        results: list[GeocodedLocation] = []
        for item in payload.get("results") or []:
            if not isinstance(item, dict):
                continue
            latitude = item.get("latitude")
            longitude = item.get("longitude")
            if latitude is None or longitude is None:
                continue
            name = str(item.get("name") or query)
            country = item.get("country")
            admin1 = item.get("admin1")
            admin2 = item.get("admin2")
            results.append(
                GeocodedLocation(
                    label=_label(name, admin2, admin1, country) or name,
                    name=name,
                    latitude=float(latitude),
                    longitude=float(longitude),
                    country=country,
                    country_code=item.get("country_code"),
                    admin_area=admin1,
                    admin_area_2=admin2,
                    timezone=item.get("timezone"),
                    population=item.get("population"),
                    source=self.name,
                )
            )
        return results[:limit]


class NominatimGeocoding:
    name = "nominatim"

    async def search(self, query: str, *, limit: int = 6) -> list[GeocodedLocation]:
        payload = await get_json(
            settings.nominatim_url,
            params={
                "q": query,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": min(max(limit, 1), 10),
            },
            headers={"User-Agent": settings.nominatim_user_agent},
            provider="Nominatim",
        )
        raw_results = payload.get("results")
        if not isinstance(raw_results, list):
            # Nominatim returns a bare list when format=json.
            if isinstance(payload, list):  # pragma: no cover - defensive
                raw_results = payload
            else:
                return []
        results: list[GeocodedLocation] = []
        for item in raw_results:
            if not isinstance(item, dict):
                continue
            address: dict[str, Any] = item.get("address") or {}
            try:
                latitude = float(item["lat"])
                longitude = float(item["lon"])
            except (KeyError, TypeError, ValueError):
                continue
            name = (
                item.get("name")
                or address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("county")
                or query
            )
            admin1 = address.get("state") or address.get("region")
            admin2 = address.get("county")
            country = address.get("country")
            results.append(
                GeocodedLocation(
                    label=item.get("display_name") or name,
                    name=str(name),
                    latitude=latitude,
                    longitude=longitude,
                    country=country,
                    country_code=(address.get("country_code") or "").upper() or None,
                    admin_area=admin1,
                    admin_area_2=admin2,
                    timezone=None,
                    population=None,
                    source=self.name,
                )
            )
        return results[:limit]


_PROVIDERS: dict[str, GeocodingProvider] = {
    "open-meteo": OpenMeteoGeocoding(),
    "nominatim": NominatimGeocoding(),
}


def get_geocoder() -> GeocodingProvider:
    return _PROVIDERS.get(settings.geocoding_provider, _PROVIDERS["open-meteo"])


def geocoder_name() -> str:
    """Human-readable name of the active provider, safe to show in the UI."""
    return {
        "open-meteo": "Open-Meteo geocoding",
        "nominatim": "OpenStreetMap Nominatim",
    }.get(settings.geocoding_provider, settings.geocoding_provider)


async def search_locations(query: str, *, limit: int = 6) -> list[GeocodedLocation]:
    cleaned = query.strip()
    if len(cleaned) < 2:
        return []
    return await get_geocoder().search(cleaned, limit=limit)


async def geocode_one(query: str) -> GeocodedLocation | None:
    """Best single match, used when the client sends a free-text place."""
    results = await search_locations(query, limit=1)
    if not results:
        raise UpstreamServiceError(
            "That place could not be found. Try a nearby larger town or city.",
            details={"query": query},
        )
    return results[0]
