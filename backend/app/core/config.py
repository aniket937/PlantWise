"""Environment-driven application configuration.

All external providers (OpenRouter, Open-Meteo, Nominatim) are configurable so
that business logic never depends on a single hard-coded vendor.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]

Environment = Literal["development", "staging", "production"]
GeocodingProvider = Literal["open-meteo", "nominatim"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application -----------------------------------------------------
    app_name: str = "PlantWise AI API"
    app_version: str = "1.0.0"
    environment: Environment = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Comma separated list in the environment, e.g. "http://a.com,http://b.com".
    # NoDecode keeps pydantic-settings from JSON-decoding the value before the
    # validator below splits it. Never a wildcard: an explicit origin list keeps
    # credentialed requests safe.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    cors_allow_credentials: bool = False

    # --- Persistence -----------------------------------------------------
    database_url: str = f"sqlite+aiosqlite:///{BACKEND_ROOT / 'plantwise.db'}"
    seed_on_startup: bool = True

    # --- AI assistant (hosted open-weight via OpenRouter) -----------------
    # Provider identity is configurable so the assistant is not coupled to a
    # single vendor. An empty OPENROUTER_API_KEY disables the assistant but
    # never the rest of the app.
    ai_provider: str = "openrouter"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemma-4-26b-a4b-it:free"
    # Tried in order by OpenRouter if the primary model errors or is rate-limited
    # (free pools are shared, so this keeps the assistant answering).
    openrouter_fallback_models: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "nvidia/nemotron-3-super-120b-a12b:free",
            "nvidia/nemotron-3.5-lightning:free",
        ]
    )
    openrouter_site_title: str = "PlantWise AI"
    openrouter_http_referer: str = ""
    ai_timeout_seconds: float = 30.0
    ai_connect_timeout_seconds: float = 5.0
    ai_temperature: float = 0.3
    ai_max_history_messages: int = 12
    ai_max_output_chars: int = 4000

    # --- Climate provider (Open-Meteo historical archive / ERA5) ---------
    open_meteo_archive_url: str = "https://archive-api.open-meteo.com/v1/archive"
    climate_baseline_start_year: int = 2015
    climate_baseline_end_year: int = 2024
    climate_cache_ttl_hours: int = 720  # 30 days

    # --- Geocoding provider ---------------------------------------------
    geocoding_provider: GeocodingProvider = "open-meteo"
    open_meteo_geocoding_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    nominatim_url: str = "https://nominatim.openstreetmap.org/search"
    nominatim_user_agent: str = "PlantWiseAI/1.0 (plant growing suitability demo)"
    geocoding_cache_ttl_hours: int = 168  # 7 days

    # --- Outbound HTTP ---------------------------------------------------
    http_timeout_seconds: float = 30.0
    http_retries: int = 2

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Accept a comma separated string as well as a JSON list."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                return value
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value

    @field_validator("openrouter_fallback_models", mode="before")
    @classmethod
    def _split_models(cls, value: object) -> object:
        """Accept a comma separated string as well as a JSON list."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                return value
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def climate_baseline_label(self) -> str:
        return f"{self.climate_baseline_start_year}-{self.climate_baseline_end_year}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
