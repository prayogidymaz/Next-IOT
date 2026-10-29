"""Workflow approval API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.types.json_types import JsonObject


class ApprovalRequestView(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    requested_by: uuid.UUID
    requested_at: datetime
    status: str
    notes: str
    approved_by: uuid.UUID | None
    approved_at: datetime | None
    approval_notes: str | None


class ApprovalPolicyView(BaseModel):
    tenant_id: uuid.UUID
    require_approval_for_production: bool
    min_approvers: int
    approver_roles_json: list[str]


class ApprovalRequestBody(BaseModel):
    notes: str = ""


class ApprovalDecisionBody(BaseModel):
    notes: str = ""


class ApprovalPolicyUpdateBody(BaseModel):
    require_approval_for_production: bool = False
    min_approvers: int = Field(default=1, ge=1, le=5)
    approver_roles_json: list[str] = Field(default_factory=lambda: ["tenant_admin", "operator"])
