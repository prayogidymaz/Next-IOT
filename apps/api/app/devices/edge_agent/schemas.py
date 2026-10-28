"""Edge agent HTTP schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class EdgeRegisterRequest(BaseModel):
    device_token: str = Field(min_length=8, max_length=128)
    device_type: str = Field(min_length=1, max_length=100)
    capabilities: list[str] = Field(default_factory=list)
    firmware_version: str | None = None


class EdgeRegisterResponse(BaseModel):
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    mqtt_topic_prefix: str


class FirmwareVersionView(BaseModel):
    id: uuid.UUID
    device_type: str
    version: str
    url: str
    checksum: str
    released_at: datetime
    stable: bool
