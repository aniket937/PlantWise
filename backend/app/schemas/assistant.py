"""AI assistant schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import ApiModel
from app.schemas.suitability import LocationInput


class ChatMessage(ApiModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class AssistantChatRequest(ApiModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=24)
    plant_slug: str | None = Field(default=None, max_length=80)
    location: LocationInput | None = None


class AssistantContext(ApiModel):
    plant_slug: str | None = None
    plant_common_name: str | None = None
    plant_scientific_name: str | None = None
    location_label: str | None = None
    applied: bool = False


class AssistantChatResponse(ApiModel):
    available: bool
    reply: str | None = None
    model: str
    unavailable_reason: str | None = None
    disclaimer: str
    context: AssistantContext
    latency_ms: int | None = None


class AssistantStatusResponse(ApiModel):
    available: bool
    model: str
    base_url_configured: bool
    detail: str
    checked_at: datetime
