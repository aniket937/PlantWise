"""Shared outbound HTTP helper.

Every external provider goes through here so timeouts, retries and error
translation live in one place, and so providers stay replaceable.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.core.errors import UpstreamServiceError

logger = logging.getLogger(__name__)

RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


def default_headers() -> dict[str, str]:
    return {"User-Agent": settings.nominatim_user_agent, "Accept": "application/json"}


def build_timeout() -> httpx.Timeout:
    return httpx.Timeout(
        settings.http_timeout_seconds,
        connect=min(10.0, settings.http_timeout_seconds),
    )


async def get_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    provider: str,
) -> dict[str, Any]:
    """GET JSON with bounded retries. Raises UpstreamServiceError on failure."""
    merged_headers = {**default_headers(), **(headers or {})}
    attempts = max(1, settings.http_retries + 1)
    last_error: str = "unknown error"

    for attempt in range(attempts):
        try:
            async with httpx.AsyncClient(timeout=build_timeout()) as client:
                response = await client.get(
                    url, params=params, headers=merged_headers, follow_redirects=True
                )
            if response.status_code in RETRYABLE_STATUS and attempt < attempts - 1:
                await asyncio.sleep(0.4 * (2**attempt))
                last_error = f"HTTP {response.status_code}"
                continue
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise UpstreamServiceError(
                    f"{provider} returned an unexpected response shape."
                )
            return payload
        except httpx.TimeoutException:
            last_error = "request timed out"
        except httpx.HTTPStatusError as exc:
            last_error = f"HTTP {exc.response.status_code}"
            if exc.response.status_code not in RETRYABLE_STATUS:
                break
        except httpx.HTTPError as exc:
            last_error = type(exc).__name__
        except ValueError:
            last_error = "response was not valid JSON"
            break

        if attempt < attempts - 1:
            await asyncio.sleep(0.4 * (2**attempt))

    logger.warning("Upstream %s request to %s failed: %s", provider, url, last_error)
    raise UpstreamServiceError(
        f"{provider} could not be reached right now.",
        details={"reason": last_error},
    )
