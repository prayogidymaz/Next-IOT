"""Apply recommendations when policy allows."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.decision.models import AutoActionPolicy, DecisionRecommendation
async def try_auto_apply(db: AsyncSession, user: CurrentUser, recommendation_id: uuid.UUID) -> DecisionRecommendation:
    rec = await db.get(DecisionRecommendation, recommendation_id)
    if rec is None or rec.tenant_id != user.tenant_id:
        raise ValueError("not found")
    policy = await db.scalar(
        select(AutoActionPolicy).where(
            AutoActionPolicy.tenant_id == user.tenant_id,
            AutoActionPolicy.trigger_type == rec.recommendation_type,
        )
    )
    if policy is None or not policy.auto_apply or rec.confidence < policy.min_confidence:
        return rec
    if policy.approval_required:
        return rec
    rec.status = "auto_applied"
    rec.applied_at = datetime.now(tz=UTC)
    rec.outcome_json = {"result": "stub_applied"}
    await db.commit()
    await db.refresh(rec)
    return rec


async def accept_recommendation(db: AsyncSession, user: CurrentUser, recommendation_id: uuid.UUID) -> DecisionRecommendation:
    rec = await db.get(DecisionRecommendation, recommendation_id)
    if rec is None or rec.tenant_id != user.tenant_id:
        raise ValueError("not found")
    rec.status = "accepted"
    rec.applied_at = datetime.now(tz=UTC)
    await db.commit()
    await db.refresh(rec)
    return rec


async def reject_recommendation(db: AsyncSession, user: CurrentUser, recommendation_id: uuid.UUID) -> DecisionRecommendation:
    rec = await db.get(DecisionRecommendation, recommendation_id)
    if rec is None or rec.tenant_id != user.tenant_id:
        raise ValueError("not found")
    rec.status = "rejected"
    await db.commit()
    await db.refresh(rec)
    return rec
