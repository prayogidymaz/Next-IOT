"""Camera gateway API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.types.json_types import JsonObject


class CameraCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    rtsp_url: str = Field(min_length=1, max_length=1024)
    username: str = ""
    password: str = ""
    location: str = ""
    farm_id: uuid.UUID | None = None
    plot_id: uuid.UUID | None = None
    physical_zone: str | None = None
    mesh_device_id: uuid.UUID | None = None
    enabled: bool = True


class CameraResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    rtsp_url: str
    location: str
    farm_id: uuid.UUID | None
    plot_id: uuid.UUID | None
    physical_zone: str | None
    mesh_device_id: uuid.UUID | None
    enabled: bool
    last_seen_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CameraSnapshotResponse(BaseModel):
    id: uuid.UUID
    camera_id: uuid.UUID
    captured_at: datetime
    image_url: str
    detection_json: JsonObject | None
    event_id: uuid.UUID | None


class MotionIngestRequest(BaseModel):
    timestamp: datetime | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[float] = Field(default_factory=list)
    snapshot_base64: str | None = None


class MotionIngestResponse(BaseModel):
    snapshot_id: uuid.UUID
    mesh_event_id: uuid.UUID | None
