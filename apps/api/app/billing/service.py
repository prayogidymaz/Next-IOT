"""Tenant-facing billing reads and mutations."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.billing.limits import parse_plan_limits
from app.billing.quota import get_message_count
from app.billing.schemas import (
    InvoiceResponse,
    PlanLimitsSchema,
    SubscriptionPlanResponse,
    TenantSubscriptionResponse,
    UsageSummaryResponse,
)
from app.billing.subscription_service import change_plan, ensure_tenant_subscription, get_tenant_limits
from app.models.device import Device
from app.models.invoice import Invoice
from app.models.payment_method import PaymentMethod
from app.models.subscription_plan import SubscriptionPlan
from app.types.redis_client import RedisClient


def _limits_schema(raw: dict[str, object]) -> PlanLimitsSchema:
    parsed = parse_plan_limits(raw)
    return PlanLimitsSchema(
        max_devices=parsed.max_devices,
        max_users=parsed.max_users,
        max_rules=parsed.max_rules,
        max_dashboards=parsed.max_dashboards,
        max_api_calls_per_day=parsed.max_api_calls_per_day,
        max_messages_per_month=parsed.max_messages_per_month,
        data_retention_days=parsed.data_retention_days,
        features=sorted(parsed.features),
    )


async def list_public_plans(db: AsyncSession) -> list[SubscriptionPlanResponse]:
    rows = await db.scalars(
        select(SubscriptionPlan).where(SubscriptionPlan.is_active).order_by(SubscriptionPlan.display_order)
    )
    return [
        SubscriptionPlanResponse(
            id=p.id,
            code=p.code,
            name=p.name,
            description=p.description,
            monthly_price_idr=p.monthly_price_idr,
            yearly_price_idr=p.yearly_price_idr,
            limits=_limits_schema(p.limits),
            display_order=p.display_order,
        )
        for p in rows.all()
    ]


async def get_subscription_summary(db: AsyncSession, user: CurrentUser) -> TenantSubscriptionResponse:
    sub = await ensure_tenant_subscription(db, user.tenant_id)
    plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == sub.plan_id))
    code = plan.code if plan else "free"
    name = plan.name if plan else "Free"
    return TenantSubscriptionResponse(
        id=sub.id,
        tenant_id=sub.tenant_id,
        plan_code=code,
        plan_name=name,
        status=sub.status,
        billing_cycle=sub.billing_cycle,
        trial_ends_at=sub.trial_ends_at,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        cancel_at_period_end=sub.cancel_at_period_end,
    )


async def get_usage_summary(db: AsyncSession, redis: RedisClient, user: CurrentUser) -> UsageSummaryResponse:
    limits = await get_tenant_limits(db, user.tenant_id)
    devices_used = int(
        await db.scalar(select(func.count()).select_from(Device).where(Device.tenant_id == user.tenant_id)) or 0
    )
    messages_used = await get_message_count(redis, user.tenant_id)
    return UsageSummaryResponse(
        devices_used=devices_used,
        devices_limit=limits.max_devices,
        messages_used=messages_used,
        messages_limit=limits.max_messages_per_month,
        api_calls_used=0,
        api_calls_limit=limits.max_api_calls_per_day,
    )


async def list_tenant_invoices(db: AsyncSession, user: CurrentUser) -> list[InvoiceResponse]:
    rows = await db.scalars(
        select(Invoice).where(Invoice.tenant_id == user.tenant_id).order_by(Invoice.created_at.desc())
    )
    return [InvoiceResponse.model_validate(row) for row in rows.all()]


async def upgrade_plan(
    db: AsyncSession,
    user: CurrentUser,
    plan_code: str,
    billing_cycle: str,
) -> TenantSubscriptionResponse:
    sub = await change_plan(db, user.tenant_id, plan_code, at_period_end=False)
    sub.billing_cycle = billing_cycle
    await db.commit()
    await db.refresh(sub)
    return await get_subscription_summary(db, user)


async def add_payment_method(
    db: AsyncSession,
    user: CurrentUser,
    *,
    provider: str,
    pm_type: str,
    details: dict[str, str],
    is_default: bool,
) -> uuid.UUID:
    if is_default:
        existing = await db.scalars(select(PaymentMethod).where(PaymentMethod.tenant_id == user.tenant_id))
        for row in existing.all():
            row.is_default = False
    pm = PaymentMethod(
        tenant_id=user.tenant_id,
        provider=provider,
        type=pm_type,
        details=details,
        is_default=is_default,
    )
    db.add(pm)
    await db.commit()
    await db.refresh(pm)
    return pm.id
