import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantSummary(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    security_tier: str
    is_active: bool
    membership_role: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TenantCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")


class TenantSwitchRequest(BaseModel):
    tenant_id: uuid.UUID


class TenantMemberResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime


class TenantMemberInviteRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(description="tenant_admin | operator | viewer")
