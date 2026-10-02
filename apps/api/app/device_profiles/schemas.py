import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.device_profiles.spec import KEY_PATTERN, ThingModelSpec
from app.models.device_profile import ProfileDomain, ProfileStatus


class DeviceProfileCreateRequest(BaseModel):
    key: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=4000)
    domain: ProfileDomain
    spec: ThingModelSpec

    @field_validator("key")
    @classmethod
    def _slug_key(cls, value: str) -> str:
        if not KEY_PATTERN.match(value):
            raise ValueError("key must use [a-z0-9_] only and be at most 64 characters")
        return value


class DeviceProfileUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    domain: ProfileDomain | None = None
    spec: ThingModelSpec | None = None


class DeviceProfileResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    key: str
    name: str
    description: str
    domain: ProfileDomain
    version: int
    status: ProfileStatus
    spec: ThingModelSpec
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssignDeviceProfileRequest(BaseModel):
    profile_id: uuid.UUID | None = Field(
        default=None,
        description="Published profile to assign; null clears assignment",
    )
