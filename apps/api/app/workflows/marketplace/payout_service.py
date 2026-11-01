"""Seller payout aggregation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.workflows.marketplace.models import MarketplacePayout, MarketplaceSeller, MarketplaceTemplatePurchase, WorkflowTemplate


async def ensure_seller(db: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID) -> MarketplaceSeller:
    row = await db.get(MarketplaceSeller, user_id)
    if row is not None:
        return row
    row = MarketplaceSeller(user_id=user_id, tenant_id=tenant_id, tier="bronze", commission_rate_percent=Decimal("15"))
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def aggregate_monthly_payouts(db: AsyncSession, period_month: str) -> list[MarketplacePayout]:
    stmt = (
        select(
            WorkflowTemplate.author_user_id,
            func.coalesce(func.sum(MarketplaceTemplatePurchase.amount_idr), 0),
        )
        .join(MarketplaceTemplatePurchase, MarketplaceTemplatePurchase.template_id == WorkflowTemplate.id)
        .where(
            MarketplaceTemplatePurchase.status == "paid",
            func.to_char(MarketplaceTemplatePurchase.created_at, "YYYY-MM") == period_month,
            WorkflowTemplate.author_user_id.is_not(None),
        )
        .group_by(WorkflowTemplate.author_user_id)
    )
    rows = await db.execute(stmt)
    created: list[MarketplacePayout] = []
    for seller_user_id, gross in rows.all():
        if seller_user_id is None:
            continue
        seller = await db.get(MarketplaceSeller, seller_user_id)
        if seller is None:
            continue
        gross_i = int(gross or 0)
        rate = float(seller.commission_rate_percent)
        commission_i = int(gross_i * rate / 100.0)
        payout = MarketplacePayout(
            seller_user_id=seller_user_id,
            period_month=period_month,
            gross_sales_idr=gross_i,
            commission_idr=commission_i,
            status="pending",
        )
        db.add(payout)
        seller.lifetime_sales_idr += gross_i
        created.append(payout)
    await db.commit()
    return created


async def mark_payout_paid(db: AsyncSession, payout_id: uuid.UUID, transaction_ref: str) -> MarketplacePayout:
    row = await db.get(MarketplacePayout, payout_id)
    if row is None:
        raise ValueError("payout not found")
    row.status = "paid"
    row.paid_at = datetime.now(tz=UTC)
    row.transaction_ref = transaction_ref
    await db.commit()
    await db.refresh(row)
    return row
