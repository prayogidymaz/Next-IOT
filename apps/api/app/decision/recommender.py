"""Rule + analytics-based recommendations (ML deep TODO)."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.decision.models import DecisionRecommendation
from app.models.device import Device, DeviceStatus
async def generate_recommendations(db: AsyncSession, user: CurrentUser) -> list[DecisionRecommendation]:
    created: list[DecisionRecommendation] = []
    offline = await db.scalar(
        select(func.count()).select_from(Device).where(Device.tenant_id == user.tenant_id, Device.status != DeviceStatus.ONLINE)
    )
    if int(offline or 0) > 3:
        row = DecisionRecommendation(
            tenant_id=user.tenant_id,
            recommendation_type="device_replacement",
            confidence=0.72,
            context_json={"offline_count": int(offline or 0)},
            status="pending",
        )
        db.add(row)
        created.append(row)
    threshold_row = DecisionRecommendation(
        tenant_id=user.tenant_id,
        recommendation_type="threshold_optimization",
        confidence=0.81,
        context_json={"hint": "Review anomaly thresholds from last 7d"},
        status="pending",
    )
    db.add(threshold_row)
    created.append(threshold_row)
    await db.commit()
    for row in created:
        await db.refresh(row)
    return created


async def list_pending(db: AsyncSession, user: CurrentUser) -> list[DecisionRecommendation]:
    rows = await db.scalars(
        select(DecisionRecommendation)
        .where(DecisionRecommendation.tenant_id == user.tenant_id, DecisionRecommendation.status == "pending")
        .order_by(DecisionRecommendation.created_at.desc())
    )
    return list(rows.all())
