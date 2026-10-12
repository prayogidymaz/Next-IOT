"""Super admin platform operations."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.auth.security import create_impersonation_access_token
from app.billing.subscription_service import change_plan, extend_trial, get_tenant_subscription
from app.config import settings
from app.models.device import Device
from app.models.invoice import Invoice
from app.models.subscription_plan import SubscriptionPlan
from app.models.super_admin_action import SuperAdminAction
from app.models.tenant import Tenant
from app.models.tenant_subscription import TenantSubscription
from app.models.user import User
from app.super_admin.audit import record_super_admin_action
from app.super_admin.schemas import (
    PlatformStatsResponse,
    RevenueGrowthPoint,
    RevenueResponse,
    SuperAdminAuditItem,
    SystemHealthResponse,
    TenantAdminItem,
    TenantDetailResponse,
)
from app.types.redis_client import RedisClient


async def platform_stats(db: AsyncSession) -> PlatformStatsResponse:
    total_tenants = int(await db.scalar(select(func.count()).select_from(Tenant)) or 0)
    active_tenants = int(await db.scalar(select(func.count()).select_from(Tenant).where(Tenant.is_active)) or 0)
    trial_subs = int(
        await db.scalar(
            select(func.count()).select_from(TenantSubscription).where(TenantSubscription.status == "trial")
        )
        or 0
    )
    active_subs = int(
        await db.scalar(
            select(func.count()).select_from(TenantSubscription).where(TenantSubscription.status == "active")
        )
        or 0
    )
    total_devices = int(await db.scalar(select(func.count()).select_from(Device)) or 0)
    mrr = await compute_mrr(db)
    month_start = datetime.now(tz=UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    mtd = await db.scalar(
        select(func.coalesce(func.sum(Invoice.total_idr), 0)).where(
            Invoice.status == "paid",
            Invoice.paid_at >= month_start,
        )
    )
    from app.super_admin.console_service import messages_today

    msg_today = await messages_today(db)
    return PlatformStatsResponse(
        total_tenants=total_tenants,
        active_tenants=active_tenants,
        trial_subscriptions=trial_subs,
        active_subscriptions=active_subs,
        total_devices=total_devices,
        mrr_idr=mrr,
        arr_idr=mrr * 12,
        revenue_mtd_idr=int(mtd or 0),
        messages_today=msg_today,
    )


async def compute_mrr(db: AsyncSession) -> int:
    rows = await db.execute(
        select(SubscriptionPlan.monthly_price_idr, func.count())
        .select_from(TenantSubscription)
        .join(SubscriptionPlan, SubscriptionPlan.id == TenantSubscription.plan_id)
        .where(TenantSubscription.status.in_(("trial", "active", "past_due")))
        .group_by(SubscriptionPlan.monthly_price_idr)
    )
    total = 0
    for price, count in rows.all():
        if price is not None:
            total += int(price) * int(count)
    return total


async def _revenue_growth_months(db: AsyncSession, months: int) -> list[RevenueGrowthPoint]:
    cutoff = datetime.now(tz=UTC) - timedelta(days=months * 31)
    rows = await db.scalars(
        select(Invoice).where(Invoice.status == "paid", Invoice.paid_at.isnot(None), Invoice.paid_at >= cutoff)
    )
    totals: dict[str, int] = {}
    for inv in rows.all():
        if inv.paid_at is None:
            continue
        key = inv.paid_at.astimezone(UTC).strftime("%Y-%m")
        totals[key] = totals.get(key, 0) + inv.total_idr
    return [RevenueGrowthPoint(month=k, revenue_idr=v) for k, v in sorted(totals.items())]


async def revenue_report(db: AsyncSession, *, months: int = 12) -> RevenueResponse:
    mrr = await compute_mrr(db)
    by_plan: dict[str, int] = {}
    rows = await db.execute(
        select(SubscriptionPlan.code, SubscriptionPlan.monthly_price_idr, func.count())
        .select_from(TenantSubscription)
        .join(SubscriptionPlan, SubscriptionPlan.id == TenantSubscription.plan_id)
        .where(TenantSubscription.status.in_(("trial", "active", "past_due")))
        .group_by(SubscriptionPlan.code, SubscriptionPlan.monthly_price_idr)
    )
    for code, price, count in rows.all():
        if price is not None:
            by_plan[str(code)] = int(price) * int(count)
    growth = await _revenue_growth_months(db, months)
    return RevenueResponse(mrr_idr=mrr, arr_idr=mrr * 12, by_plan=by_plan, growth_12m=growth)


async def list_tenants_admin(
    db: AsyncSession,
    *,
    status_filter: str | None = None,
    plan_code: str | None = None,
    search: str | None = None,
) -> list[TenantAdminItem]:
    query = select(Tenant).order_by(Tenant.created_at.desc())
    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.where(or_(func.lower(Tenant.name).like(term), func.lower(Tenant.slug).like(term)))
    tenants = await db.scalars(query)
    items: list[TenantAdminItem] = []
    for tenant in tenants.all():
        summary = await _tenant_admin_item(db, tenant)
        if status_filter == "suspended":
            if tenant.is_active:
                continue
        elif status_filter and summary.subscription_status != status_filter:
            continue
        if plan_code and summary.plan_code != plan_code:
            continue
        items.append(summary)
    return items


async def _tenant_admin_item(db: AsyncSession, tenant: Tenant) -> TenantAdminItem:
    sub = await get_tenant_subscription(db, tenant.id)
    plan_code_val: str | None = None
    sub_status: str | None = sub.status if sub else None
    if sub is not None:
        plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == sub.plan_id))
        plan_code_val = plan.code if plan else None
    device_count = int(
        await db.scalar(select(func.count()).select_from(Device).where(Device.tenant_id == tenant.id)) or 0
    )
    user_count = int(
        await db.scalar(select(func.count()).select_from(User).where(User.tenant_id == tenant.id)) or 0
    )
    return TenantAdminItem(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        is_active=tenant.is_active,
        plan_code=plan_code_val,
        subscription_status=sub_status,
        device_count=device_count,
        user_count=user_count,
        created_at=tenant.created_at,
    )


async def get_tenant_detail(db: AsyncSession, tenant_id: uuid.UUID) -> TenantDetailResponse:
    tenant = await db.scalar(select(Tenant).where(Tenant.id == tenant_id))
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    summary = await _tenant_admin_item(db, tenant)
    sub = await get_tenant_subscription(db, tenant_id)
    audit_rows = await db.scalars(
        select(SuperAdminAction)
        .where(SuperAdminAction.target_tenant_id == tenant_id)
        .order_by(SuperAdminAction.created_at.desc())
        .limit(20)
    )
    audit_entries = [
        SuperAdminAuditItem(id=row.id, action=row.action, detail=row.detail, created_at=row.created_at)
        for row in audit_rows.all()
    ]
    return TenantDetailResponse(
        **summary.model_dump(),
        trial_ends_at=sub.trial_ends_at if sub else None,
        audit_entries=audit_entries,
    )


async def suspend_tenant(
    db: AsyncSession,
    user: CurrentUser,
    tenant_id: uuid.UUID,
    *,
    reason: str | None = None,
) -> None:
    tenant = await db.scalar(select(Tenant).where(Tenant.id == tenant_id))
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    tenant.is_active = False
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="suspend_tenant",
        target_tenant_id=tenant_id,
        detail={"reason": reason} if reason else {},
    )
    await db.commit()


async def unsuspend_tenant(db: AsyncSession, user: CurrentUser, tenant_id: uuid.UUID) -> None:
    tenant = await db.scalar(select(Tenant).where(Tenant.id == tenant_id))
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    tenant.is_active = True
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="unsuspend_tenant",
        target_tenant_id=tenant_id,
        detail={},
    )
    await db.commit()


async def extend_trial_admin(db: AsyncSession, user: CurrentUser, tenant_id: uuid.UUID, days: int) -> None:
    await extend_trial(db, tenant_id, days)
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="extend_trial",
        target_tenant_id=tenant_id,
        detail={"days": days},
    )
    await db.commit()


async def change_plan_admin(
    db: AsyncSession,
    user: CurrentUser,
    tenant_id: uuid.UUID,
    plan_code: str,
    *,
    prorate: bool,
) -> None:
    await change_plan(db, tenant_id, plan_code, at_period_end=not prorate)
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="change_plan",
        target_tenant_id=tenant_id,
        detail={"plan_code": plan_code, "prorate": prorate},
    )
    await db.commit()


async def impersonate_tenant(db: AsyncSession, user: CurrentUser, tenant_id: uuid.UUID) -> str:
    tenant = await db.scalar(select(Tenant).where(Tenant.id == tenant_id))
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    actor = await db.scalar(select(User).where(User.id == user.user_id))
    if actor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="impersonate_tenant",
        target_tenant_id=tenant_id,
        detail={"actor_email": actor.email},
    )
    await db.commit()
    return create_impersonation_access_token(user_id=actor.id, tenant_id=tenant_id, role=actor.role)


async def system_health(db: AsyncSession, redis: RedisClient) -> SystemHealthResponse:
    api_status = "ok"
    db_status = "ok"
    redis_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "degraded"
    try:
        await redis.ping()
    except Exception:
        redis_status = "degraded"
    mqtt_sub = "ok" if settings.mqtt_subscriber_enabled else "stopped"
    mqtt_pub = "ok" if settings.mqtt_publisher_enabled else "stopped"
    from app.super_admin.console_service import emqx_health_status

    emqx_status = await emqx_health_status()
    return SystemHealthResponse(
        api=api_status,
        database=db_status,
        redis=redis_status,
        emqx=emqx_status,
        scheduler="ok",
        mqtt_subscriber=mqtt_sub,
        mqtt_publisher=mqtt_pub,
        checked_at=datetime.now(tz=UTC),
    )
