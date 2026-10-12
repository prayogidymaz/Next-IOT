"""Pydantic schemas for Step 9C super-admin features."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class EmailTemplateVariable(BaseModel):
    name: str
    description: str


class EmailTemplateResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    subject: str
    body_html: str
    body_text: str | None
    variables: list[EmailTemplateVariable]
    is_active: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmailTemplateUpdateRequest(BaseModel):
    subject: str | None = None
    body_html: str | None = None
    body_text: str | None = None
    is_active: bool | None = None


class EmailTemplatePreviewRequest(BaseModel):
    sample_variables: dict[str, object] = Field(default_factory=dict)


class EmailTemplatePreviewResponse(BaseModel):
    subject: str
    body_html: str
    body_text: str | None


class EmailTemplateTestRequest(BaseModel):
    recipient_email: str
    sample_variables: dict[str, object] = Field(default_factory=dict)


class SupportTicketListItem(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID | None
    subject: str
    category: str
    priority: str
    status: str
    assigned_to: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupportTicketMessageResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID | None
    is_internal: bool
    body: str
    attachments: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class SupportTicketDetailResponse(SupportTicketListItem):
    description: str
    messages: list[SupportTicketMessageResponse]


class SupportTicketCreateRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1)
    category: str = Field(default="other")
    priority: str = Field(default="normal")


class SupportTicketAssignRequest(BaseModel):
    user_id: uuid.UUID


class SupportTicketStatusRequest(BaseModel):
    status: str


class SupportTicketMessageCreateRequest(BaseModel):
    body: str = Field(min_length=1)
    is_internal: bool = False
    attachments: list[str] = Field(default_factory=list)


class SupportTicketStatsResponse(BaseModel):
    open: int
    in_progress: int
    waiting_customer: int
    resolved_today: int
    avg_resolution_hours: float


class PartnerResponse(BaseModel):
    id: uuid.UUID
    name: str
    contact_email: str
    tier: str
    commission_percent: float
    status: str
    referral_code: str
    company_name: str
    joined_at: datetime

    model_config = {"from_attributes": True}


class PartnerCreateRequest(BaseModel):
    name: str
    contact_email: str = ""
    contact_phone: str = ""
    contact_person: str = ""
    company_name: str = ""
    address: str = ""
    tax_id: str = ""
    tier: str = "silver"
    commission_percent: float = 10.0
    status: str = "pending"
    notes: str = ""


class PartnerUpdateRequest(BaseModel):
    name: str | None = None
    contact_email: str | None = None
    tier: str | None = None
    commission_percent: float | None = None
    status: str | None = None
    notes: str | None = None


class PartnerReferralResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    referred_at: datetime
    total_revenue_idr: int
    total_commission_idr: int


class PartnerCommissionResponse(BaseModel):
    id: uuid.UUID
    period_month: date
    total_commission_idr: int
    status: str
    paid_at: datetime | None

    model_config = {"from_attributes": True}


class CommissionCalculateRequest(BaseModel):
    period_month: date


class BackupResponse(BaseModel):
    id: uuid.UUID
    backup_type: str
    size_bytes: int
    status: str
    started_at: datetime
    completed_at: datetime | None
    triggered_by: uuid.UUID | None
    expires_at: datetime | None

    model_config = {"from_attributes": True}


class BackupTriggerRequest(BaseModel):
    backup_type: str = Field(pattern="^(full|database_only|config_only)$")


class BackupRestoreRequest(BaseModel):
    confirm_token: str


class ImpersonationSessionResponse(BaseModel):
    id: uuid.UUID
    super_admin_user_id: uuid.UUID | None
    tenant_id: uuid.UUID | None
    started_at: datetime
    ended_at: datetime | None
    action_count: int = 0
    duration_seconds: int | None = None


class ImpersonationActionResponse(BaseModel):
    id: uuid.UUID
    action: str
    resource: str
    detail: dict[str, object]
    created_at: datetime

    model_config = {"from_attributes": True}
