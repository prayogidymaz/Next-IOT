import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DeviceRegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    device_type: str = Field(min_length=1, max_length=100)
    metadata: dict[str, str] = Field(default_factory=dict)


class DeviceMetadataItem(BaseModel):
    key: str
    value: str


class DeviceResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    device_type: str
    status: str
    last_seen_at: datetime | None
    metadata: list[DeviceMetadataItem]
    created_at: datetime

    model_config = {"from_attributes": True}


class DeviceRegisterResponse(BaseModel):
    device: DeviceResponse
    provisioning_token: str
    provisioning_expires_in_hours: int


class DeviceProvisionRequest(BaseModel):
    provisioning_token: str


class DeviceCredentialsResponse(BaseModel):
    client_id: str
    client_secret: str
    device_id: uuid.UUID
    status: str


class HeartbeatRequest(BaseModel):
    firmware_version: str | None = Field(default=None, max_length=100)
    ip: str | None = Field(default=None, max_length=45)
    telemetry: dict[str, str | float | int | bool] | None = None


class HeartbeatResponse(BaseModel):
    device_id: uuid.UUID
    status: str
    last_seen_at: datetime


class DeviceStatusPatchRequest(BaseModel):
    status: str = Field(description="Target status: provisioned (reactivate) or deactivated")
