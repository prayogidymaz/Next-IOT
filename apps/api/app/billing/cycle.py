"""Billing cycle automation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.invoice_service import create_invoice_for_subscription
from app.config import settings
from app.models.invoice import Invoice
from app.models.subscription_plan import SubscriptionPlan
from app.models.tenant_subscription import TenantSubscription


async def run_billing_cycle(db: AsyncSession) -> dict[str, int]:
    today = datetime.now(tz=UTC).date()
    subs = await db.scalars(
        select(TenantSubscription).where(
            TenantSubscription.status.in_(("trial", "active", "past_due")),
        )
    )
    invoices_created = 0
    past_due_marked = 0
    expired_marked = 0
    for sub in subs.all():
        plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == sub.plan_id))
        if plan is None:
            continue
        if sub.current_period_end is not None and sub.current_period_end.date() <= today:
            period_start = today
            if sub.billing_cycle == "yearly":
                period_end = period_start + timedelta(days=365)
            else:
                period_end = period_start + timedelta(days=30)
            await create_invoice_for_subscription(
                db,
                tenant_id=sub.tenant_id,
                subscription=sub,
                plan=plan,
                period_start=period_start,
                period_end=period_end,
            )
            sub.current_period_start = datetime.combine(period_start, datetime.min.time(), tzinfo=UTC)
            sub.current_period_end = datetime.combine(period_end, datetime.min.time(), tzinfo=UTC)
            if sub.status == "trial":
                sub.status = "active"
            invoices_created += 1
        overdue = await db.scalar(
            select(Invoice)
            .where(
                Invoice.subscription_id == sub.id,
                Invoice.status == "pending",
                Invoice.due_date < today,
            )
            .order_by(Invoice.due_date.desc())
            .limit(1)
        )
        if overdue is not None:
            days_overdue = (today - overdue.due_date).days
            if days_overdue >= settings.subscription_expired_days:
                sub.status = "expired"
                expired_marked += 1
            elif days_overdue >= settings.subscription_past_due_grace_days:
                sub.status = "past_due"
                past_due_marked += 1
    await db.commit()
    return {
        "invoices_created": invoices_created,
        "past_due_marked": past_due_marked,
        "expired_marked": expired_marked,
    }


async def mark_invoice_paid(
    db: AsyncSession,
    invoice_id: uuid.UUID,
    *,
    provider: str,
    reference: str,
) -> Invoice | None:
    inv = await db.scalar(select(Invoice).where(Invoice.id == invoice_id))
    if inv is None:
        return None
    if inv.status == "paid":
        return inv
    inv.status = "paid"
    inv.paid_at = datetime.now(tz=UTC)
    inv.payment_provider = provider
    inv.payment_reference = reference
    sub = await db.scalar(select(TenantSubscription).where(TenantSubscription.id == inv.subscription_id))
    if sub is not None and sub.status in {"past_due", "trial"}:
        sub.status = "active"
    await db.commit()
    await db.refresh(inv)
    return inv
