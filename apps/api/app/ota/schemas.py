import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FirmwareReleaseResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    version: str
    target_device_category: str
    file_url: str
    checksum_sha256: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OtaRolloutResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    device_name: str
    status: str
    reported_at: datetime | None
    created_at: datetime


class OtaPublishResponse(BaseModel):
    release: FirmwareReleaseResponse
    targeted_devices: int
    rollouts_created: int


class OtaUpdateCheckResponse(BaseModel):
    update_available: bool
    version: str | None = None
    file_url: str | None = None
    checksum_sha256: str | None = None
    release_id: uuid.UUID | None = None


class OtaRolloutStatusPatch(BaseModel):
    status: str = Field(description="pending | downloading | applied | failed")
