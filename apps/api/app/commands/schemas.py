import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class CommandTypeEnum(StrEnum):
    GO_TO_WAYPOINT = "GO_TO_WAYPOINT"
    GO_TO_MISSION = "GO_TO_MISSION"
    RTL = "RTL"
    TAKEOFF = "TAKEOFF"
    LAND = "LAND"


class DeviceCommandRequest(BaseModel):
    command_type: CommandTypeEnum
    params: dict[str, Any] = Field(default_factory=dict)

    @field_validator("params")
    @classmethod
    def params_must_be_object(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("params must be an object")
        return value


class DeviceCommandResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    command_type: str
    params: dict[str, Any]
    status: str
    created_at: datetime
    dispatched_at: datetime | None = None

    model_config = {"from_attributes": True}
