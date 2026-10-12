"""Extended super-admin console operations (analytics, audit, commercial)."""

from __future__ import annotations

import csv
import io
import uuid
from datetime import UTC, date, datetime, timedelta

import httpx
from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.config import settings
from app.models.audit_log import AuditLog
from app.models.device import Device
from app.models.feature_flag import FeatureFlag
from app.models.invoice import Invoice
from app.models.platform_announcement import PlatformAnnouncement
from app.models.platform_setting import PlatformSetting
from app.models.promo_code import PromoCode
from app.models.subscription_plan import SubscriptionPlan
from app.models.super_admin_action import SuperAdminAction
from app.models.tenant import Tenant
from app.models.tenant_subscription import TenantSubscription
from app.models.tenant_usage_daily import TenantUsageDaily
from app.models.user import User
from app.mqtt_auth.emqx_rule_setup import _auth as emqx_basic_auth
from app.super_admin.audit import record_super_admin_action
from app.super_admin.schemas import (
    AnalyticsDeepDiveResponse,
    AnnouncementCreateRequest,
    AnnouncementResponse,
    AuditLogEntry,
    ChurnByPlanItem,
    CohortRetentionRow,
    FeatureFlagResponse,
    FeatureFlagUpdateRequest,
    FinanceExportMeta,
    HealthScoreItem,
    MqttMonitorResponse,
    PlatformSettingsResponse,
    PlatformSettingsUpdateRequest,
    PromoCodeCreateRequest,
    PromoCodeResponse,
    RateLimitTenantRow,
    SystemLogLine,
    TopicVolumeItem,
    WatchListItem,
)

DEFAULT_PLATFORM_SETTINGS: dict[str, dict[str, object]] = {
    "general": {
        "platform_name": "Next-IoT",
        "support_email": "support@nextiot.com",
        "timezone": "Asia/Jakarta",
    },
    "email": {"smtp_host": "", "smtp_port": 587, "from_address": ""},
    "payment": {"midtrans_server_key": "", "xendit_secret_key": ""},
    "mqtt": {"broker_url": "mqtt://emqx:1883", "max_connections_per_tenant": 500},
    "security": {"session_timeout_minutes": 60, "password_min_length": 12, "require_2fa": False},
    "notifications": {"default_email": True, "default_push": False},
}

DEFAULT_FEATURE_FLAGS: list[tuple[str, str]] = [
    ("beta_dashboard_v2", "Next-gen tenant dashboard"),
    ("ai_insights", "AI telemetry insights"),
    ("export_excel", "Excel export for reports"),
    ("advanced_rules", "Multi-step rule engine"),
]


async def _ensure_feature_flags(db: AsyncSession) -> None:
    existing = await db.scalar(select(func.count()).select_from(FeatureFlag))
    if int(existing or 0) > 0:
        return
    for name, description in DEFAULT_FEATURE_FLAGS:
        db.add(FeatureFlag(name=name, description=description))
    await db.flush()


async def list_audit_log(
    db: AsyncSession,
    *,
    from_ts: datetime | None,
    to_ts: datetime | None,
    actor: str | None,
    action: str | None,
    search: str | None,
    limit: int = 200,
) -> list[AuditLogEntry]:
    entries: list[AuditLogEntry] = []
    q_audit = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
    if from_ts:
        q_audit = q_audit.where(AuditLog.timestamp >= from_ts)
    if to_ts:
        q_audit = q_audit.where(AuditLog.timestamp <= to_ts)
    if actor:
        q_audit = q_audit.where(AuditLog.actor_email.ilike(f"%{actor}%"))
    if action:
        q_audit = q_audit.where(AuditLog.action == action)
    if search:
        term = f"%{search}%"
        q_audit = q_audit.where(or_(AuditLog.resource_target.ilike(term), AuditLog.actor_email.ilike(term)))
    for row in (await db.scalars(q_audit)).all():
        entries.append(
            AuditLogEntry(
                id=row.id,
                timestamp=row.timestamp,
                actor_type="user",
                actor_label=row.actor_email,
                action=row.action,
                target=row.resource_target or (str(row.tenant_id) if row.tenant_id else ""),
                details={"status": row.status, "tenant_id": str(row.tenant_id) if row.tenant_id else None},
                source="audit_logs",
            )
        )
    q_sa = select(SuperAdminAction).order_by(SuperAdminAction.created_at.desc()).limit(limit)
    if from_ts:
        q_sa = q_sa.where(SuperAdminAction.created_at >= from_ts)
    if to_ts:
        q_sa = q_sa.where(SuperAdminAction.created_at <= to_ts)
    if action:
        q_sa = q_sa.where(SuperAdminAction.action == action)
    for sa_row in (await db.scalars(q_sa)).all():
        actor_label = "system"
        if sa_row.actor_user_id:
            user = await db.scalar(select(User).where(User.id == sa_row.actor_user_id))
            if user:
                actor_label = user.email
        if actor and actor.lower() not in actor_label.lower():
            continue
        target = str(sa_row.target_tenant_id) if sa_row.target_tenant_id else ""
        if search and search not in target and search.lower() not in actor_label.lower():
            continue
        entries.append(
            AuditLogEntry(
                id=sa_row.id,
                timestamp=sa_row.created_at,
                actor_type="super_admin",
                actor_label=actor_label,
                action=sa_row.action,
                target=target,
                details=sa_row.detail,
                source="super_admin_actions",
            )
        )
    entries.sort(key=lambda e: e.timestamp, reverse=True)
    return entries[:limit]


def audit_log_csv(rows: list[AuditLogEntry]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["timestamp", "actor", "action", "target", "source"])
    for row in rows:
        writer.writerow([row.timestamp.isoformat(), row.actor_label, row.action, row.target, row.source])
    return buf.getvalue()


async def messages_today(db: AsyncSession) -> int:
    today = datetime.now(tz=UTC).date()
    total = await db.scalar(
        select(func.coalesce(func.sum(TenantUsageDaily.messages_count), 0)).where(TenantUsageDaily.usage_date == today)
    )
    return int(total or 0)


async def analytics_deep_dive(db: AsyncSession, *, months: int = 12) -> AnalyticsDeepDiveResponse:
    from app.super_admin.service import compute_mrr, revenue_report

    revenue = await revenue_report(db, months=months)
    mrr = await compute_mrr(db)
    tenant_count = int(await db.scalar(select(func.count()).select_from(Tenant)) or 1)
    arpa = mrr // max(tenant_count, 1)
    ltv_estimate = arpa * 24
    cohort = await cohort_retention(db, months=min(months, 12))
    churn = await churn_by_plan(db)
    device_growth = await _device_growth_months(db, months)
    message_volume = await _message_volume_months(db, months)
    return AnalyticsDeepDiveResponse(
        mrr_trend=revenue.growth_12m,
        cohort_retention=cohort,
        churn_by_plan=churn,
        arpa_idr=arpa,
        ltv_estimate_idr=ltv_estimate,
        device_growth=device_growth,
        message_volume=message_volume,
    )


async def cohort_retention(db: AsyncSession, months: int) -> list[CohortRetentionRow]:
    cutoff = datetime.now(tz=UTC) - timedelta(days=months * 31)
    tenants = await db.scalars(select(Tenant).where(Tenant.created_at >= cutoff))
    rows: list[CohortRetentionRow] = []
    for tenant in tenants.all():
        cohort_month = tenant.created_at.astimezone(UTC).strftime("%Y-%m")
        active_months: list[str] = []
        usage = await db.scalars(
            select(TenantUsageDaily)
            .where(TenantUsageDaily.tenant_id == tenant.id, TenantUsageDaily.messages_count > 0)
            .order_by(TenantUsageDaily.usage_date)
        )
        for u in usage.all():
            key = u.usage_date.strftime("%Y-%m")
            if key not in active_months:
                active_months.append(key)
        rows.append(CohortRetentionRow(cohort_month=cohort_month, tenant_id=tenant.id, active_months=active_months))
    return rows[:100]


async def churn_by_plan(db: AsyncSession) -> list[ChurnByPlanItem]:
    items: list[ChurnByPlanItem] = []
    plans = await db.scalars(select(SubscriptionPlan))
    for plan in plans.all():
        total = int(
            await db.scalar(
                select(func.count())
                .select_from(TenantSubscription)
                .where(TenantSubscription.plan_id == plan.id)
            )
            or 0
        )
        churned = int(
            await db.scalar(
                select(func.count())
                .select_from(TenantSubscription)
                .where(TenantSubscription.plan_id == plan.id, TenantSubscription.status == "cancelled")
            )
            or 0
        )
        rate = (churned / total * 100.0) if total else 0.0
        items.append(ChurnByPlanItem(plan_code=plan.code, churn_rate_percent=round(rate, 2), subscribers=total))
    return items


async def _device_growth_months(db: AsyncSession, months: int) -> list[dict[str, int | str]]:
    cutoff = datetime.now(tz=UTC) - timedelta(days=months * 31)
    rows = await db.scalars(select(Device).where(Device.created_at >= cutoff))
    totals: dict[str, int] = {}
    for dev in rows.all():
        key = dev.created_at.astimezone(UTC).strftime("%Y-%m")
        totals[key] = totals.get(key, 0) + 1
    return [{"month": k, "devices": v} for k, v in sorted(totals.items())]


async def _message_volume_months(db: AsyncSession, months: int) -> list[dict[str, int | str]]:
    cutoff = date.today() - timedelta(days=months * 31)
    rows = await db.execute(
        select(TenantUsageDaily.usage_date, func.sum(TenantUsageDaily.messages_count))
        .where(TenantUsageDaily.usage_date >= cutoff)
        .group_by(TenantUsageDaily.usage_date)
        .order_by(TenantUsageDaily.usage_date)
    )
    monthly: dict[str, int] = {}
    for usage_date, msg_sum in rows.all():
        key = usage_date.strftime("%Y-%m")
        monthly[key] = monthly.get(key, 0) + int(msg_sum or 0)
    return [{"month": k, "messages": v} for k, v in sorted(monthly.items())]


async def tenant_health_scores(db: AsyncSession) -> list[HealthScoreItem]:
    tenants = await db.scalars(select(Tenant).order_by(Tenant.created_at.desc()).limit(200))
    items: list[HealthScoreItem] = []
    today = date.today()
    week_ago = today - timedelta(days=7)
    for tenant in tenants.all():
        score = 50
        recent_usage = await db.scalars(
            select(TenantUsageDaily)
            .where(TenantUsageDaily.tenant_id == tenant.id, TenantUsageDaily.usage_date >= week_ago)
            .order_by(TenantUsageDaily.usage_date)
        )
        usage_rows = recent_usage.all()
        if len(usage_rows) >= 2:
            growth = usage_rows[-1].messages_count - usage_rows[0].messages_count
            if growth > 0:
                score += 15
            elif growth < 0:
                score -= 15
        device_count = int(
            await db.scalar(select(func.count()).select_from(Device).where(Device.tenant_id == tenant.id)) or 0
        )
        if device_count > 0:
            score += 10
        sub = await db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant.id))
        if sub and sub.status in ("active", "trial"):
            score += 10
        if sub and sub.status == "past_due":
            score -= 25
        if not tenant.is_active:
            score = min(score, 20)
        score = max(0, min(100, score))
        at_risk = score < 40
        items.append(
            HealthScoreItem(
                tenant_id=tenant.id,
                tenant_name=tenant.name,
                tenant_slug=tenant.slug,
                score=score,
                at_risk=at_risk,
                device_count=device_count,
            )
        )
    items.sort(key=lambda i: i.score)
    return items


async def watch_list(db: AsyncSession) -> list[WatchListItem]:
    scores = await tenant_health_scores(db)
    items: list[WatchListItem] = []
    for row in scores:
        if row.at_risk:
            items.append(
                WatchListItem(
                    tenant_id=row.tenant_id,
                    tenant_name=row.tenant_name,
                    reason="health_score_low",
                    severity="high",
                )
            )
    overdue = await db.scalars(
        select(Invoice).where(Invoice.status == "past_due").order_by(Invoice.created_at.desc()).limit(10)
    )
    for inv in overdue.all():
        items.append(
            WatchListItem(
                tenant_id=inv.tenant_id,
                tenant_name=str(inv.tenant_id),
                reason="overdue_invoice",
                severity="medium",
            )
        )
    return items[:20]


async def rate_limit_rows(db: AsyncSession, *, period_hours: int = 24) -> list[RateLimitTenantRow]:
    since = date.today() - timedelta(days=1 if period_hours <= 24 else 7)
    tenants = await db.scalars(select(Tenant).limit(100))
    rows: list[RateLimitTenantRow] = []
    for tenant in tenants.all():
        agg = await db.execute(
            select(
                func.coalesce(func.sum(TenantUsageDaily.api_calls_count), 0),
                func.coalesce(func.sum(TenantUsageDaily.messages_count), 0),
            ).where(TenantUsageDaily.tenant_id == tenant.id, TenantUsageDaily.usage_date >= since)
        )
        api_calls, mqtt_msgs = agg.one()
        api_i = int(api_calls or 0)
        mqtt_i = int(mqtt_msgs or 0)
        quota_pct = min(100.0, (api_i / 100_000) * 100) if api_i else 0.0
        hits = 1 if api_i > 80_000 else 0
        rows.append(
            RateLimitTenantRow(
                tenant_id=tenant.id,
                tenant_name=tenant.name,
                api_calls_period=api_i,
                mqtt_messages_period=mqtt_i,
                quota_usage_percent=round(quota_pct, 1),
                rate_limit_hits=hits,
            )
        )
    rows.sort(key=lambda r: r.api_calls_period, reverse=True)
    return rows


async def mqtt_monitor_stats() -> MqttMonitorResponse:
    base = settings.emqx_dashboard_url.rstrip("/")
    if not settings.emqx_api_key.strip():
        return MqttMonitorResponse(
            connections=0,
            messages_per_sec=0.0,
            publish_per_sec=0.0,
            subscribe_per_sec=0.0,
            dropped_messages=0,
            errors=0,
            top_topics=[],
            top_clients=[],
            status="unconfigured",
        )
    try:
        async with httpx.AsyncClient(timeout=settings.emqx_dashboard_timeout_seconds) as client:
            auth = emqx_basic_auth()
            nodes = await client.get(f"{base}/api/v5/nodes", auth=auth)
            nodes.raise_for_status()
            data = nodes.json()
            node_list = data.get("data", data) if isinstance(data, dict) else data
            connections = 0
            if isinstance(node_list, list) and node_list:
                connections = int(node_list[0].get("connections", 0) if isinstance(node_list[0], dict) else 0)
            return MqttMonitorResponse(
                connections=connections,
                messages_per_sec=0.0,
                publish_per_sec=0.0,
                subscribe_per_sec=0.0,
                dropped_messages=0,
                errors=0,
                top_topics=[TopicVolumeItem(topic="devices/+/telemetry", count=connections)],
                top_clients=[],
                status="ok",
            )
    except httpx.HTTPError:
        return MqttMonitorResponse(
            connections=0,
            messages_per_sec=0.0,
            publish_per_sec=0.0,
            subscribe_per_sec=0.0,
            dropped_messages=0,
            errors=1,
            top_topics=[],
            top_clients=[],
            status="degraded",
        )


async def tail_system_logs(
    db: AsyncSession,
    *,
    service: str,
    level: str,
    lines: int,
    search: str | None,
) -> list[SystemLogLine]:
    out: list[SystemLogLine] = []
    level_upper = level.upper()
    audit = await db.scalars(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(lines))
    for row in audit.all():
        mapped = "ERROR" if row.status != "success" else "INFO"
        if level_upper != "ALL" and mapped != level_upper and level_upper != "WARNING":
            if level_upper == "ERROR" and mapped != "ERROR":
                continue
            if level_upper == "INFO" and mapped != "INFO":
                continue
        msg = f"{row.action} {row.resource_target}"
        if search and search.lower() not in msg.lower():
            continue
        out.append(
            SystemLogLine(
                timestamp=row.timestamp,
                service=service,
                level=mapped,
                message=msg,
            )
        )
    if len(out) < lines:
        out.append(
            SystemLogLine(
                timestamp=datetime.now(tz=UTC),
                service=service,
                level="INFO",
                message=f"Log tail for {service} (audit-backed; live docker logs not attached)",
            )
        )
    return out[:lines]


async def list_announcements(db: AsyncSession) -> list[AnnouncementResponse]:
    rows = await db.scalars(select(PlatformAnnouncement).order_by(PlatformAnnouncement.created_at.desc()))
    return [AnnouncementResponse.model_validate(r) for r in rows.all()]


async def create_announcement(
    db: AsyncSession,
    user: CurrentUser,
    payload: AnnouncementCreateRequest,
) -> AnnouncementResponse:
    row = PlatformAnnouncement(
        title=payload.title,
        body=payload.body,
        announcement_type=payload.announcement_type,
        target_filter=payload.target_filter,
        start_at=payload.start_at,
        expires_at=payload.expires_at,
        published=payload.published,
    )
    db.add(row)
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="create_announcement",
        target_tenant_id=None,
        detail={"title": payload.title},
    )
    await db.commit()
    await db.refresh(row)
    return AnnouncementResponse.model_validate(row)


async def list_promo_codes(db: AsyncSession) -> list[PromoCodeResponse]:
    rows = await db.scalars(select(PromoCode).order_by(PromoCode.created_at.desc()))
    return [PromoCodeResponse.model_validate(r) for r in rows.all()]


async def create_promo_code(db: AsyncSession, user: CurrentUser, payload: PromoCodeCreateRequest) -> PromoCodeResponse:
    existing = await db.scalar(select(PromoCode).where(PromoCode.code == payload.code.upper()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Code already exists")
    row = PromoCode(
        code=payload.code.upper(),
        discount_type=payload.discount_type,
        discount_value=payload.discount_value,
        valid_plans=payload.valid_plans,
        max_uses=payload.max_uses,
        expires_at=payload.expires_at,
        active=True,
    )
    db.add(row)
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="create_promo_code",
        target_tenant_id=None,
        detail={"code": row.code},
    )
    await db.commit()
    await db.refresh(row)
    return PromoCodeResponse.model_validate(row)


async def validate_promo_code(db: AsyncSession, code: str) -> PromoCodeResponse:
    row = await db.scalar(select(PromoCode).where(PromoCode.code == code.upper(), PromoCode.active.is_(True)))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid promo code")
    if row.expires_at and row.expires_at < datetime.now(tz=UTC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Promo code expired")
    if row.max_uses is not None and row.used_count >= row.max_uses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Promo code exhausted")
    return PromoCodeResponse.model_validate(row)


async def get_platform_settings(db: AsyncSession) -> PlatformSettingsResponse:
    rows = await db.scalars(select(PlatformSetting))
    merged: dict[str, dict[str, object]] = {k: dict(v) for k, v in DEFAULT_PLATFORM_SETTINGS.items()}
    for row in rows.all():
        merged[row.key] = row.value
    return PlatformSettingsResponse(sections=merged)


async def update_platform_settings(
    db: AsyncSession,
    user: CurrentUser,
    payload: PlatformSettingsUpdateRequest,
) -> PlatformSettingsResponse:
    for key, value in payload.sections.items():
        existing = await db.scalar(select(PlatformSetting).where(PlatformSetting.key == key))
        if existing:
            existing.value = value
        else:
            db.add(PlatformSetting(key=key, value=value))
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="update_platform_settings",
        target_tenant_id=None,
        detail={"keys": list(payload.sections.keys())},
    )
    await db.commit()
    return await get_platform_settings(db)


async def list_feature_flags(db: AsyncSession) -> list[FeatureFlagResponse]:
    await _ensure_feature_flags(db)
    await db.commit()
    rows = await db.scalars(select(FeatureFlag).order_by(FeatureFlag.name))
    return [FeatureFlagResponse.model_validate(r) for r in rows.all()]


async def update_feature_flag(
    db: AsyncSession,
    user: CurrentUser,
    flag_id: uuid.UUID,
    payload: FeatureFlagUpdateRequest,
) -> FeatureFlagResponse:
    row = await db.scalar(select(FeatureFlag).where(FeatureFlag.id == flag_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature flag not found")
    if payload.enabled_global is not None:
        row.enabled_global = payload.enabled_global
    if payload.rollout_percent is not None:
        row.rollout_percent = payload.rollout_percent
    if payload.tenant_overrides is not None:
        row.tenant_overrides = payload.tenant_overrides
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="update_feature_flag",
        target_tenant_id=None,
        detail={"name": row.name, "enabled_global": row.enabled_global},
    )
    await db.commit()
    await db.refresh(row)
    return FeatureFlagResponse.model_validate(row)


async def finance_export_csv(db: AsyncSession, *, from_ts: datetime, to_ts: datetime) -> tuple[str, FinanceExportMeta]:
    invoices = await db.scalars(
        select(Invoice)
        .where(
            Invoice.status == "paid",
            Invoice.paid_at.isnot(None),
            Invoice.paid_at >= from_ts,
            Invoice.paid_at <= to_ts,
        )
        .order_by(Invoice.paid_at)
    )
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["invoice_id", "tenant_id", "paid_at", "total_idr", "status"])
    total = 0
    count = 0
    for inv in invoices.all():
        paid_label = inv.paid_at.isoformat() if inv.paid_at else ""
        writer.writerow([str(inv.id), str(inv.tenant_id), paid_label, inv.total_idr, inv.status])
        total += inv.total_idr
        count += 1
    meta = FinanceExportMeta(invoice_count=count, total_revenue_idr=total, from_ts=from_ts, to_ts=to_ts)
    return buf.getvalue(), meta


async def emqx_health_status() -> str:
    stats = await mqtt_monitor_stats()
    return stats.status if stats.status != "unconfigured" else "unknown"
