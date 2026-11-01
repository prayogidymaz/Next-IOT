"""Recommendation outcome feedback."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.decision.models import DecisionRecommendation
from app.types.json_types import JsonObject


async def record_outcome(db: AsyncSession, user: CurrentUser, recommendation_id: uuid.UUID, outcome: JsonObject) -> DecisionRecommendation:
    rec = await db.get(DecisionRecommendation, recommendation_id)
    if rec is None or rec.tenant_id != user.tenant_id:
        raise ValueError("not found")
    rec.outcome_json = outcome
    await db.commit()
    await db.refresh(rec)
    return rec


async def success_rate(db: AsyncSession, user: CurrentUser) -> dict[str, float]:
    total = await db.scalar(
        select(func.count()).select_from(DecisionRecommendation).where(DecisionRecommendation.tenant_id == user.tenant_id)
    )
    accepted = await db.scalar(
        select(func.count())
        .select_from(DecisionRecommendation)
        .where(DecisionRecommendation.tenant_id == user.tenant_id, DecisionRecommendation.status.in_(["accepted", "auto_applied"]))
    )
    t = int(total or 0)
    a = int(accepted or 0)
    return {"total": float(t), "accepted": float(a), "success_rate": (a / t) if t else 0.0}
