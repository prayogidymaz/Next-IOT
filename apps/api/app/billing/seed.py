"""Idempotent subscription plan seed."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.plan_definitions import plan_seed_rows
from app.models.subscription_plan import SubscriptionPlan


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) else None


def _required_int(value: object, default: int) -> int:
    return value if isinstance(value, int) else default


async def seed_plans(db: AsyncSession) -> int:
    created = 0
    for row in plan_seed_rows():
        code_raw = row.get("code")
        if not isinstance(code_raw, str):
            continue
        existing = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == code_raw))
        if existing is not None:
            continue
        limits_raw = row.get("limits")
        limits: dict[str, object] = {}
        if isinstance(limits_raw, dict):
            for key, val in limits_raw.items():
                if isinstance(key, str):
                    limits[key] = val
        db.add(
            SubscriptionPlan(
                id=uuid.uuid4(),
                code=code_raw,
                name=str(row.get("name", code_raw)),
                description=str(row["description"]) if row.get("description") is not None else None,
                monthly_price_idr=_optional_int(row.get("monthly_price_idr")),
                yearly_price_idr=_optional_int(row.get("yearly_price_idr")),
                limits=limits,
                is_active=True,
                display_order=_required_int(row.get("display_order"), 0),
            )
        )
        created += 1
    if created:
        await db.commit()
    return created
