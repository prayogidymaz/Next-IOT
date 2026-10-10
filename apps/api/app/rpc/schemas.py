"""Pydantic schemas for device RPC API."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class DeviceRpcCreateRequest(BaseModel):
    method: str = Field(min_length=1, max_length=64)
    params: dict[str, JsonValue] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=30, ge=1, le=300)


class DeviceRpcCreateResponse(BaseModel):
    status: str
    response: JsonValue | None = None
    reason: str | None = None
    request_id: uuid.UUID | None = None


class DeviceRpcItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    method: str
    params: dict[str, JsonValue]
    status: str
    response_json: JsonValue | None
    error_message: str | None
    timeout_seconds: int
    requested_at: datetime
    delivered_at: datetime | None
    completed_at: datetime | None


class DeviceRpcListResponse(BaseModel):
    items: list[DeviceRpcItem]
