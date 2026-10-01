import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, JsonValue, field_validator


class CommandTypeEnum(StrEnum):
    GO_TO_WAYPOINT = "GO_TO_WAYPOINT"
    GO_TO_MISSION = "GO_TO_MISSION"
    RTL = "RTL"
    TAKEOFF = "TAKEOFF"
    LAND = "LAND"
    RETURN_TO_HOME = "RETURN_TO_HOME"
    EMERGENCY_LAND = "EMERGENCY_LAND"
    RELAY_ON = "RELAY_ON"
    RELAY_OFF = "RELAY_OFF"
    SET_ACTUATOR = "SET_ACTUATOR"


class DeviceCommandRequest(BaseModel):
    command_type: CommandTypeEnum
    params: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("params")
    @classmethod
    def params_must_be_object(cls, value: dict[str, JsonValue]) -> dict[str, JsonValue]:
        if not isinstance(value, dict):
            raise ValueError("params must be an object")
        return value


class DeviceCommandResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    command_type: str
    params: dict[str, JsonValue]
    status: str
    created_at: datetime
    dispatched_at: datetime | None = None

    model_config = {"from_attributes": True}
