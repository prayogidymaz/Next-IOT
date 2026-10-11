"""Super admin API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PlatformStatsResponse(BaseModel):
    total_tenants: int
    active_tenants: int
    trial_subscriptions: int
    active_subscriptions: int
    total_devices: int
    mrr_idr: int
    revenue_mtd_idr: int


class TenantAdminItem(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    is_active: bool
    plan_code: str | None
    subscription_status: str | None
    device_count: int
    created_at: datetime


class ExtendTrialRequest(BaseModel):
    days: int = Field(ge=1, le=365)


class ChangePlanAdminRequest(BaseModel):
    plan_code: str
    prorate: bool = False


class RevenueResponse(BaseModel):
    mrr_idr: int
    arr_idr: int
    by_plan: dict[str, int]


class SystemHealthResponse(BaseModel):
    api: str
    database: str
    redis: str
    emqx: str
    scheduler: str


class ImpersonateResponse(BaseModel):
    access_token: str
    tenant_id: uuid.UUID
