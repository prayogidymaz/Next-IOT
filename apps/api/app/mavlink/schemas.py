from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class MavlinkCommandEnum(StrEnum):
    ARM = "ARM"
    DISARM = "DISARM"
    RTL = "RTL"
    LAND = "LAND"
    WAYPOINT = "WAYPOINT"


class MavlinkTelemetrySnapshot(BaseModel):
    mavlink_connected: bool = False
    protocol_version: str = "2.0"
    autopilot: str | None = None
    vehicle_type: str | None = None
    metrics: dict[str, float | int] = Field(default_factory=dict)
    last_message_type: str | None = None


class MavlinkDecodeRequest(BaseModel):
    data_b64: str
    device_id: str | None = None


class MavlinkDecodeResponse(BaseModel):
    messages: list[str]
    snapshot: MavlinkTelemetrySnapshot


class MavlinkEncodeRequest(BaseModel):
    command: MavlinkCommandEnum
    target_system: int = Field(default=1, ge=1, le=255)
    target_component: int = Field(default=1, ge=1, le=255)
    params: dict[str, Any] = Field(default_factory=dict)


class MavlinkEncodeResponse(BaseModel):
    command: str
    data_b64: str
    byte_length: int


class MavlinkStatusResponse(BaseModel):
    device_id: str | None = None
    connected: bool = False
    protocol_version: str = "2.0"
    autopilot: str | None = None
    last_heartbeat_at: str | None = None
    metrics: dict[str, float | int] = Field(default_factory=dict)
