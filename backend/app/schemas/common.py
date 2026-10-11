"""Shared schema primitives."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DataSource(ApiModel):
    """Provenance for a single documented fact."""

    label: str
    url: str | None = None
    note: str | None = None


class ErrorDetail(ApiModel):
    field: str | None = None
    message: str


class ErrorPayload(ApiModel):
    code: str
    message: str
    details: list[ErrorDetail] | None = None


class ErrorResponse(ApiModel):
    error: ErrorPayload
