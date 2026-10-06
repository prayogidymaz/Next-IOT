from __future__ import annotations

import uuid
from datetime import datetime

from app.models.device_claim_token import DeviceClaimToken
from pydantic import BaseModel, Field


class DeviceClaimTokenCreateRequest(BaseModel):
    device_name: str = Field(min_length=1, max_length=255)
    device_type: str = Field(min_length=1, max_length=100)
    device_category: str = Field(min_length=1, max_length=64)
    profile_id: uuid.UUID | None = None
    ttl_hours: int = Field(default=24, ge=1, le=168)


class DeviceClaimTokenResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    claim_token: str
    device_name: str
    device_type: str
    device_category: str
    profile_id: uuid.UUID | None
    expires_at: datetime
    claimed_at: datetime | None
    claimed_device_id: uuid.UUID | None
    created_at: datetime
    qr_code_url: str

    @classmethod
    def from_model(cls, row: DeviceClaimToken, *, qr_code_url: str) -> DeviceClaimTokenResponse:
        return cls(
            id=row.id,
            tenant_id=row.tenant_id,
            claim_token=row.claim_token,
            device_name=row.device_name,
            device_type=row.device_type,
            device_category=row.device_category,
            profile_id=row.profile_id,
            expires_at=row.expires_at,
            claimed_at=row.claimed_at,
            claimed_device_id=row.claimed_device_id,
            created_at=row.created_at,
            qr_code_url=qr_code_url,
        )


class DeviceClaimResultResponse(BaseModel):
    device_id: uuid.UUID
    access_token: str
    mqtt_broker_url: str
    client_id: str
    topic_prefix: str
