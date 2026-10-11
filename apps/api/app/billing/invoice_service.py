"""Invoice creation and PDF stub URLs."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.invoice import Invoice
from app.models.subscription_plan import SubscriptionPlan
from app.models.tenant_subscription import TenantSubscription


def _tax_amount(subtotal: int) -> int:
    rate = settings.invoice_tax_percent / Decimal("100")
    tax = (Decimal(subtotal) * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(tax)


async def _next_invoice_number(db: AsyncSession) -> str:
    year = datetime.now(tz=UTC).year
    prefix = f"INV-{year}-"
    count = await db.scalar(
        select(func.count()).select_from(Invoice).where(Invoice.invoice_number.like(f"{prefix}%"))
    )
    seq = int(count or 0) + 1
    return f"{prefix}{seq:05d}"


def invoice_pdf_path(invoice_id: uuid.UUID) -> str:
    return f"/api/v1/billing/invoices/{invoice_id}/pdf"


async def create_invoice_for_subscription(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    subscription: TenantSubscription,
    plan: SubscriptionPlan,
    period_start: date,
    period_end: date,
) -> Invoice:
    if subscription.billing_cycle == "yearly":
        subtotal = plan.yearly_price_idr or plan.monthly_price_idr or 0
        description = f"{plan.name} (yearly)"
    else:
        subtotal = plan.monthly_price_idr or 0
        description = f"{plan.name} (monthly)"
    tax = _tax_amount(subtotal)
    total = subtotal + tax
    line_items: list[dict[str, object]] = [
        {"description": description, "qty": 1, "unit_price": subtotal, "total": subtotal}
    ]
    inv = Invoice(
        tenant_id=tenant_id,
        subscription_id=subscription.id,
        invoice_number=await _next_invoice_number(db),
        period_start=period_start,
        period_end=period_end,
        subtotal_idr=subtotal,
        tax_idr=tax,
        total_idr=total,
        status="pending" if total > 0 else "paid",
        due_date=period_start + timedelta(days=7),
        line_items=line_items,
        pdf_url=None,
    )
    db.add(inv)
    await db.flush()
    inv.pdf_url = invoice_pdf_path(inv.id)
    await db.flush()
    return inv
