"""Super admin platform operations."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.auth.security import create_access_token
from app.billing.subscription_service import change_plan, extend_trial, get_tenant_subscription
from app.models.device import Device
from app.models.invoice import Invoice
from app.models.subscription_plan import SubscriptionPlan
from app.models.tenant import Tenant
from app.models.tenant_subscription import TenantSubscription
from app.models.user import User
from app.super_admin.audit import record_super_admin_action
from app.super_admin.schemas import PlatformStatsResponse, RevenueResponse, SystemHealthResponse, TenantAdminItem
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
    return PlatformStatsResponse(
        total_tenants=total_tenants,
        active_tenants=active_tenants,
        trial_subscriptions=trial_subs,
        active_subscriptions=active_subs,
        total_devices=total_devices,
        mrr_idr=mrr,
        revenue_mtd_idr=int(mtd or 0),
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


async def revenue_report(db: AsyncSession) -> RevenueResponse:
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
    return RevenueResponse(mrr_idr=mrr, arr_idr=mrr * 12, by_plan=by_plan)


async def list_tenants_admin(
    db: AsyncSession,
    *,
    status_filter: str | None = None,
    plan_code: str | None = None,
) -> list[TenantAdminItem]:
    tenants = await db.scalars(select(Tenant).order_by(Tenant.created_at.desc()))
    items: list[TenantAdminItem] = []
    for tenant in tenants.all():
        sub = await get_tenant_subscription(db, tenant.id)
        plan_code_val: str | None = None
        sub_status: str | None = sub.status if sub else None
        if sub is not None:
            plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == sub.plan_id))
            plan_code_val = plan.code if plan else None
        if status_filter and sub_status != status_filter:
            continue
        if plan_code and plan_code_val != plan_code:
            continue
        device_count = int(
            await db.scalar(select(func.count()).select_from(Device).where(Device.tenant_id == tenant.id)) or 0
        )
        items.append(
            TenantAdminItem(
                id=tenant.id,
                name=tenant.name,
                slug=tenant.slug,
                is_active=tenant.is_active,
                plan_code=plan_code_val,
                subscription_status=sub_status,
                device_count=device_count,
                created_at=tenant.created_at,
            )
        )
    return items


async def suspend_tenant(db: AsyncSession, user: CurrentUser, tenant_id: uuid.UUID) -> None:
    tenant = await db.scalar(select(Tenant).where(Tenant.id == tenant_id))
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    tenant.is_active = False
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="suspend_tenant",
        target_tenant_id=tenant_id,
        detail={},
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
    return create_access_token(user_id=actor.id, tenant_id=tenant_id, role=actor.role)


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
    return SystemHealthResponse(
        api=api_status,
        database=db_status,
        redis=redis_status,
        emqx="unknown",
        scheduler="ok" if True else "stopped",
    )
