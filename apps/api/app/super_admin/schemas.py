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
    arr_idr: int = 0
    revenue_mtd_idr: int
    messages_today: int = 0


class TenantAdminItem(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    is_active: bool
    plan_code: str | None
    subscription_status: str | None
    device_count: int
    user_count: int
    created_at: datetime


class SuperAdminAuditItem(BaseModel):
    id: uuid.UUID
    action: str
    detail: dict[str, object]
    created_at: datetime


class TenantDetailResponse(TenantAdminItem):
    trial_ends_at: datetime | None
    audit_entries: list[SuperAdminAuditItem]


class SuspendTenantRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class ExtendTrialRequest(BaseModel):
    days: int = Field(ge=1, le=365)


class ChangePlanAdminRequest(BaseModel):
    plan_code: str
    prorate: bool = False


class RevenueGrowthPoint(BaseModel):
    month: str
    revenue_idr: int


class RevenueResponse(BaseModel):
    mrr_idr: int
    arr_idr: int
    by_plan: dict[str, int]
    growth_12m: list[RevenueGrowthPoint] = Field(default_factory=list)


class SystemHealthResponse(BaseModel):
    api: str
    database: str
    redis: str
    emqx: str
    scheduler: str
    mqtt_subscriber: str
    mqtt_publisher: str
    checked_at: datetime


class ImpersonateResponse(BaseModel):
    access_token: str
    tenant_id: uuid.UUID
    impersonation_session_id: uuid.UUID


class AuditLogEntry(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    actor_type: str
    actor_label: str
    action: str
    target: str
    details: dict[str, object]
    source: str


class CohortRetentionRow(BaseModel):
    cohort_month: str
    tenant_id: uuid.UUID
    active_months: list[str]


class ChurnByPlanItem(BaseModel):
    plan_code: str
    churn_rate_percent: float
    subscribers: int


class AnalyticsDeepDiveResponse(BaseModel):
    mrr_trend: list[RevenueGrowthPoint]
    cohort_retention: list[CohortRetentionRow]
    churn_by_plan: list[ChurnByPlanItem]
    arpa_idr: int
    ltv_estimate_idr: int
    device_growth: list[dict[str, int | str]]
    message_volume: list[dict[str, int | str]]


class HealthScoreItem(BaseModel):
    tenant_id: uuid.UUID
    tenant_name: str
    tenant_slug: str
    score: int
    at_risk: bool
    device_count: int


class WatchListItem(BaseModel):
    tenant_id: uuid.UUID
    tenant_name: str
    reason: str
    severity: str


class TopicVolumeItem(BaseModel):
    topic: str
    count: int


class MqttMonitorResponse(BaseModel):
    connections: int
    messages_per_sec: float
    publish_per_sec: float
    subscribe_per_sec: float
    dropped_messages: int
    errors: int
    top_topics: list[TopicVolumeItem]
    top_clients: list[TopicVolumeItem]
    status: str


class RateLimitTenantRow(BaseModel):
    tenant_id: uuid.UUID
    tenant_name: str
    api_calls_period: int
    mqtt_messages_period: int
    quota_usage_percent: float
    rate_limit_hits: int


class SystemLogLine(BaseModel):
    timestamp: datetime
    service: str
    level: str
    message: str


class AnnouncementResponse(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    announcement_type: str
    target_filter: dict[str, object]
    start_at: datetime | None
    expires_at: datetime | None
    published: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AnnouncementCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1)
    announcement_type: str = Field(default="info", pattern="^(info|warning|critical)$")
    target_filter: dict[str, object] = Field(default_factory=dict)
    start_at: datetime | None = None
    expires_at: datetime | None = None
    published: bool = False


class PromoCodeResponse(BaseModel):
    id: uuid.UUID
    code: str
    discount_type: str
    discount_value: int
    valid_plans: list[str]
    max_uses: int | None
    used_count: int
    expires_at: datetime | None
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PromoCodeCreateRequest(BaseModel):
    code: str = Field(min_length=3, max_length=64)
    discount_type: str = Field(pattern="^(percent|fixed_idr)$")
    discount_value: int = Field(ge=1)
    valid_plans: list[str] = Field(default_factory=list)
    max_uses: int | None = Field(default=None, ge=1)
    expires_at: datetime | None = None


class PlatformSettingsResponse(BaseModel):
    sections: dict[str, dict[str, object]]


class PlatformSettingsUpdateRequest(BaseModel):
    sections: dict[str, dict[str, object]]


class FeatureFlagResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    enabled_global: bool
    rollout_percent: int
    tenant_overrides: dict[str, bool]
    updated_at: datetime

    model_config = {"from_attributes": True}


class FeatureFlagUpdateRequest(BaseModel):
    enabled_global: bool | None = None
    rollout_percent: int | None = Field(default=None, ge=0, le=100)
    tenant_overrides: dict[str, bool] | None = None


class FinanceExportMeta(BaseModel):
    invoice_count: int
    total_revenue_idr: int
    from_ts: datetime
    to_ts: datetime
