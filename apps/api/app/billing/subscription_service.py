"""Tenant subscription lifecycle."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.limits import PlanLimits, parse_plan_limits
from app.config import settings
from app.models.subscription_plan import SubscriptionPlan
from app.models.tenant_subscription import TenantSubscription


async def get_plan_by_code(db: AsyncSession, code: str) -> SubscriptionPlan:
    plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == code, SubscriptionPlan.is_active))
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{code}' not found")
    return plan


async def get_tenant_subscription(db: AsyncSession, tenant_id: uuid.UUID) -> TenantSubscription | None:
    sub: TenantSubscription | None = await db.scalar(
        select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id)
    )
    return sub


async def get_tenant_limits(db: AsyncSession, tenant_id: uuid.UUID) -> PlanLimits:
    sub = await get_tenant_subscription(db, tenant_id)
    if sub is None:
        plan = await get_plan_by_code(db, "free")
        return parse_plan_limits(plan.limits)
    loaded: SubscriptionPlan | None = await db.scalar(
        select(SubscriptionPlan).where(SubscriptionPlan.id == sub.plan_id)
    )
    if loaded is None:
        return parse_plan_limits({})
    return parse_plan_limits(loaded.limits)


async def ensure_tenant_subscription(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    *,
    plan_code: str = "free",
) -> TenantSubscription:
    existing = await get_tenant_subscription(db, tenant_id)
    if existing is not None:
        return existing
    plan = await get_plan_by_code(db, plan_code)
    now = datetime.now(tz=UTC)
    trial_end = now + timedelta(days=settings.subscription_trial_days)
    period_end = trial_end
    sub = TenantSubscription(
        tenant_id=tenant_id,
        plan_id=plan.id,
        status="trial",
        billing_cycle="monthly",
        trial_ends_at=trial_end,
        current_period_start=now,
        current_period_end=period_end,
    )
    db.add(sub)
    await db.flush()
    return sub


async def change_plan(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    plan_code: str,
    *,
    at_period_end: bool = False,
) -> TenantSubscription:
    sub = await get_tenant_subscription(db, tenant_id)
    if sub is None:
        sub = await ensure_tenant_subscription(db, tenant_id)
    plan = await get_plan_by_code(db, plan_code)
    if at_period_end:
        sub.cancel_at_period_end = False
        sub.plan_id = plan.id
        if sub.status in {"trial", "active"}:
            sub.status = "active"
        await db.flush()
        return sub
    sub.plan_id = plan.id
    sub.status = "active"
    sub.cancel_at_period_end = False
    await db.flush()
    return sub


async def extend_trial(db: AsyncSession, tenant_id: uuid.UUID, days: int) -> TenantSubscription:
    sub = await get_tenant_subscription(db, tenant_id)
    if sub is None:
        sub = await ensure_tenant_subscription(db, tenant_id)
    base = sub.trial_ends_at or datetime.now(tz=UTC)
    sub.trial_ends_at = base + timedelta(days=days)
    if sub.current_period_end is None or sub.current_period_end < sub.trial_ends_at:
        sub.current_period_end = sub.trial_ends_at
    sub.status = "trial"
    await db.flush()
    return sub


async def mark_trial_expired_if_needed(db: AsyncSession, sub: TenantSubscription) -> None:
    if sub.status != "trial" or sub.trial_ends_at is None:
        return
    if datetime.now(tz=UTC) >= sub.trial_ends_at:
        sub.status = "expired"
