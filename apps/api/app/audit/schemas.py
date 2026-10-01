import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AuditLogItem(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    actor_id: uuid.UUID | None
    actor_email: str
    tenant_id: uuid.UUID | None
    action: str
    resource_target: str
    ip_address: str | None
    status: str

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    items: list[AuditLogItem]
    total: int
    page: int
    page_size: int


class AuditLogExportQuery(BaseModel):
    action: str | None = None
    actor: str | None = Field(default=None, description="Search actor email or resource")
    start_time: datetime | None = None
    end_time: datetime | None = None
