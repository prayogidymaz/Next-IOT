"""Super admin console API."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Query, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy import select

from app.auth.dependencies import RequireSuperAdmin
from app.billing.cycle import run_billing_cycle
from app.billing.schemas import InvoiceResponse
from app.deps import DbSession, RedisDep
from app.models.invoice import Invoice
from app.super_admin import console_service, service
from app.super_admin.schemas import (
    AnalyticsDeepDiveResponse,
    AnnouncementCreateRequest,
    AnnouncementResponse,
    AuditLogEntry,
    ChangePlanAdminRequest,
    ChurnByPlanItem,
    CohortRetentionRow,
    ExtendTrialRequest,
    FeatureFlagResponse,
    FeatureFlagUpdateRequest,
    HealthScoreItem,
    ImpersonateResponse,
    MqttMonitorResponse,
    PlatformSettingsResponse,
    PlatformSettingsUpdateRequest,
    PlatformStatsResponse,
    PromoCodeCreateRequest,
    PromoCodeResponse,
    RateLimitTenantRow,
    RevenueResponse,
    SuspendTenantRequest,
    SystemHealthResponse,
    SystemLogLine,
    TenantAdminItem,
    TenantDetailResponse,
    WatchListItem,
)
from app.super_admin.agriculture_router import router as agriculture_admin_router
from app.super_admin.step9c_router import router as step9c_router

router = APIRouter(prefix="/api/v1/super-admin", tags=["super-admin"])


@router.get("/stats", response_model=PlatformStatsResponse)
async def get_platform_stats(user: RequireSuperAdmin, db: DbSession) -> PlatformStatsResponse:
    return await service.platform_stats(db)


@router.get("/tenants", response_model=list[TenantAdminItem])
async def list_tenants(
    user: RequireSuperAdmin,
    db: DbSession,
    status: str | None = Query(default=None),
    plan: str | None = Query(default=None),
    q: str | None = Query(default=None),
) -> list[TenantAdminItem]:
    return await service.list_tenants_admin(db, status_filter=status, plan_code=plan, search=q)


@router.get("/tenants/{tenant_id}", response_model=TenantDetailResponse)
async def get_tenant_detail(tenant_id: uuid.UUID, user: RequireSuperAdmin, db: DbSession) -> TenantDetailResponse:
    return await service.get_tenant_detail(db, tenant_id)


@router.post("/tenants/{tenant_id}/suspend", status_code=204, response_class=Response)
async def suspend_tenant(
    tenant_id: uuid.UUID,
    user: RequireSuperAdmin,
    db: DbSession,
    payload: SuspendTenantRequest | None = None,
) -> Response:
    reason = payload.reason if payload is not None else None
    await service.suspend_tenant(db, user, tenant_id, reason=reason)
    return Response(status_code=204)


@router.post("/tenants/{tenant_id}/unsuspend", status_code=204, response_class=Response)
async def unsuspend_tenant(tenant_id: uuid.UUID, user: RequireSuperAdmin, db: DbSession) -> Response:
    await service.unsuspend_tenant(db, user, tenant_id)
    return Response(status_code=204)


@router.post("/tenants/{tenant_id}/extend-trial", status_code=204, response_class=Response)
async def extend_trial(
    tenant_id: uuid.UUID,
    payload: ExtendTrialRequest,
    user: RequireSuperAdmin,
    db: DbSession,
) -> Response:
    await service.extend_trial_admin(db, user, tenant_id, payload.days)
    return Response(status_code=204)


@router.post("/tenants/{tenant_id}/change-plan", status_code=204, response_class=Response)
async def change_plan(
    tenant_id: uuid.UUID,
    payload: ChangePlanAdminRequest,
    user: RequireSuperAdmin,
    db: DbSession,
) -> Response:
    await service.change_plan_admin(db, user, tenant_id, payload.plan_code, prorate=payload.prorate)
    return Response(status_code=204)


@router.post("/tenants/{tenant_id}/impersonate", response_model=ImpersonateResponse)
async def impersonate(tenant_id: uuid.UUID, user: RequireSuperAdmin, db: DbSession) -> ImpersonateResponse:
    return await service.impersonate_tenant(db, user, tenant_id)


@router.get("/invoices", response_model=list[InvoiceResponse])
async def list_invoices(
    user: RequireSuperAdmin,
    db: DbSession,
    status: str | None = Query(default=None),
) -> list[InvoiceResponse]:
    query = select(Invoice).order_by(Invoice.created_at.desc())
    if status:
        query = query.where(Invoice.status == status)
    rows = await db.scalars(query)
    return [InvoiceResponse.model_validate(row) for row in rows.all()]


@router.get("/revenue", response_model=RevenueResponse)
async def get_revenue(
    user: RequireSuperAdmin,
    db: DbSession,
    months: int = Query(default=12, ge=1, le=24),
) -> RevenueResponse:
    return await service.revenue_report(db, months=months)


@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health(user: RequireSuperAdmin, db: DbSession, redis: RedisDep) -> SystemHealthResponse:
    return await service.system_health(db, redis)


@router.post("/billing-cycle/run")
async def run_billing_cycle_manual(user: RequireSuperAdmin, db: DbSession) -> dict[str, int]:
    return await run_billing_cycle(db)


@router.get("/audit-log", response_model=list[AuditLogEntry])
async def get_audit_log(
    user: RequireSuperAdmin,
    db: DbSession,
    from_ts: datetime | None = Query(default=None),
    to_ts: datetime | None = Query(default=None),
    actor: str | None = None,
    action: str | None = None,
    q: str | None = None,
    limit: int = Query(default=200, ge=1, le=500),
) -> list[AuditLogEntry]:
    return await console_service.list_audit_log(
        db, from_ts=from_ts, to_ts=to_ts, actor=actor, action=action, search=q, limit=limit
    )


@router.get("/audit-log/export")
async def export_audit_log(
    user: RequireSuperAdmin,
    db: DbSession,
    from_ts: datetime | None = Query(default=None),
    to_ts: datetime | None = Query(default=None),
) -> PlainTextResponse:
    rows = await console_service.list_audit_log(db, from_ts=from_ts, to_ts=to_ts, actor=None, action=None, search=None)
    return PlainTextResponse(content=console_service.audit_log_csv(rows), media_type="text/csv")


@router.get("/analytics/deep-dive", response_model=AnalyticsDeepDiveResponse)
async def analytics_deep_dive(
    user: RequireSuperAdmin, db: DbSession, months: int = Query(default=12, ge=1, le=24)
) -> AnalyticsDeepDiveResponse:
    return await console_service.analytics_deep_dive(db, months=months)


@router.get("/analytics/cohort", response_model=list[CohortRetentionRow])
async def analytics_cohort(
    user: RequireSuperAdmin, db: DbSession, months: int = Query(default=12, ge=1, le=24)
) -> list[CohortRetentionRow]:
    return await console_service.cohort_retention(db, months=months)


@router.get("/analytics/churn-rate", response_model=list[ChurnByPlanItem])
async def analytics_churn(user: RequireSuperAdmin, db: DbSession) -> list[ChurnByPlanItem]:
    return await console_service.churn_by_plan(db)


@router.get("/health-scores", response_model=list[HealthScoreItem])
async def health_scores(user: RequireSuperAdmin, db: DbSession) -> list[HealthScoreItem]:
    return await console_service.tenant_health_scores(db)


@router.get("/watch-list", response_model=list[WatchListItem])
async def watch_list(user: RequireSuperAdmin, db: DbSession) -> list[WatchListItem]:
    return await console_service.watch_list(db)


@router.get("/mqtt/stats", response_model=MqttMonitorResponse)
async def mqtt_stats(user: RequireSuperAdmin) -> MqttMonitorResponse:
    return await console_service.mqtt_monitor_stats()


@router.get("/rate-limits", response_model=list[RateLimitTenantRow])
async def rate_limits(
    user: RequireSuperAdmin, db: DbSession, period: str = Query(default="24h", pattern="^(1h|24h|7d)$")
) -> list[RateLimitTenantRow]:
    hours = 1 if period == "1h" else 24 if period == "24h" else 168
    return await console_service.rate_limit_rows(db, period_hours=hours)


@router.get("/logs/tail", response_model=list[SystemLogLine])
async def logs_tail(
    user: RequireSuperAdmin,
    db: DbSession,
    service_name: str = Query(default="api", alias="service"),
    level: str = Query(default="ERROR"),
    lines: int = Query(default=100, ge=1, le=500),
    q: str | None = None,
) -> list[SystemLogLine]:
    return await console_service.tail_system_logs(db, service=service_name, level=level, lines=lines, search=q)


@router.get("/announcements", response_model=list[AnnouncementResponse])
async def list_announcements(user: RequireSuperAdmin, db: DbSession) -> list[AnnouncementResponse]:
    return await console_service.list_announcements(db)


@router.post("/announcements", response_model=AnnouncementResponse, status_code=201)
async def create_announcement(
    user: RequireSuperAdmin, db: DbSession, payload: AnnouncementCreateRequest
) -> AnnouncementResponse:
    return await console_service.create_announcement(db, user, payload)


@router.get("/promo-codes", response_model=list[PromoCodeResponse])
async def list_promo_codes(user: RequireSuperAdmin, db: DbSession) -> list[PromoCodeResponse]:
    return await console_service.list_promo_codes(db)


@router.post("/promo-codes", response_model=PromoCodeResponse, status_code=201)
async def create_promo_code(
    user: RequireSuperAdmin, db: DbSession, payload: PromoCodeCreateRequest
) -> PromoCodeResponse:
    return await console_service.create_promo_code(db, user, payload)


@router.get("/promo-codes/{code}/validate", response_model=PromoCodeResponse)
async def validate_promo_code(user: RequireSuperAdmin, db: DbSession, code: str) -> PromoCodeResponse:
    return await console_service.validate_promo_code(db, code)


@router.get("/platform-settings", response_model=PlatformSettingsResponse)
async def get_platform_settings(user: RequireSuperAdmin, db: DbSession) -> PlatformSettingsResponse:
    return await console_service.get_platform_settings(db)


@router.put("/platform-settings", response_model=PlatformSettingsResponse)
async def put_platform_settings(
    user: RequireSuperAdmin, db: DbSession, payload: PlatformSettingsUpdateRequest
) -> PlatformSettingsResponse:
    return await console_service.update_platform_settings(db, user, payload)


@router.get("/feature-flags", response_model=list[FeatureFlagResponse])
async def get_feature_flags(user: RequireSuperAdmin, db: DbSession) -> list[FeatureFlagResponse]:
    return await console_service.list_feature_flags(db)


@router.put("/feature-flags/{flag_id}", response_model=FeatureFlagResponse)
async def put_feature_flag(
    user: RequireSuperAdmin,
    db: DbSession,
    flag_id: uuid.UUID,
    payload: FeatureFlagUpdateRequest,
) -> FeatureFlagResponse:
    return await console_service.update_feature_flag(db, user, flag_id, payload)


@router.get("/finance/export")
async def finance_export(
    user: RequireSuperAdmin,
    db: DbSession,
    from_ts: datetime | None = Query(default=None),
    to_ts: datetime | None = Query(default=None),
    format: str = Query(default="csv", pattern="^(csv|xlsx)$"),
) -> PlainTextResponse:
    end = to_ts or datetime.now(tz=UTC)
    start = from_ts or (end - timedelta(days=30))
    csv_body, _meta = await console_service.finance_export_csv(db, from_ts=start, to_ts=end)
    if format == "xlsx":
        return PlainTextResponse(
            content=csv_body,
            media_type="text/csv",
            headers={"X-Format-Note": "xlsx requires openpyxl; returned csv"},
        )
    return PlainTextResponse(content=csv_body, media_type="text/csv")


router.include_router(step9c_router)
router.include_router(agriculture_admin_router)
