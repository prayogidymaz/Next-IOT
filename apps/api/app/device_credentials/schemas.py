from __future__ import annotations

import uuid
from datetime import datetime

from app.models.device_credential import CredentialType, DeviceCredential
from pydantic import BaseModel, ConfigDict


class DeviceCredentialPublicResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    credential_type: CredentialType
    client_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_connected_at: datetime | None
    rotated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, credential: DeviceCredential) -> DeviceCredentialPublicResponse:
        return cls(
            id=credential.id,
            device_id=credential.device_id,
            tenant_id=credential.tenant_id,
            credential_type=credential.credential_type,
            client_id=credential.client_id,
            is_active=credential.is_active,
            created_at=credential.created_at,
            updated_at=credential.updated_at,
            last_connected_at=credential.last_connected_at,
            rotated_at=credential.rotated_at,
        )


class DeviceCredentialCreateResponse(DeviceCredentialPublicResponse):
    access_token: str
    client_secret: str | None = None

    @classmethod
    def from_created(
        cls,
        credential: DeviceCredential,
        *,
        access_token: str,
        client_secret: str | None,
    ) -> DeviceCredentialCreateResponse:
        base = DeviceCredentialPublicResponse.from_model(credential)
        return cls(
            **base.model_dump(),
            access_token=access_token,
            client_secret=client_secret,
        )
