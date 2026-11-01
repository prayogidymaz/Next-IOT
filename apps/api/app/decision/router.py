"""AI decision engine API."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.dependencies import RequireAuth
from app.decision import auto_action, outcome_tracker, recommender
from app.decision.models import AutoActionPolicy, DecisionRecommendation
from app.deps import DbSession
from app.types.json_types import JsonObject
from sqlalchemy import select

router = APIRouter(prefix="/api/v1/decisions", tags=["decisions"])


class RecommendationView(BaseModel):
    id: uuid.UUID
    recommendation_type: str
    confidence: float
    status: str
    context_json: dict[str, object]

    model_config = {"from_attributes": True}


class PolicyCreate(BaseModel):
    trigger_type: str
    min_confidence: float = Field(ge=0, le=1)
    auto_apply: bool = False
    approval_required: bool = True


class PolicyView(BaseModel):
    id: uuid.UUID
    trigger_type: str
    min_confidence: float
    auto_apply: bool
    approval_required: bool

    model_config = {"from_attributes": True}


@router.get("/recommendations", response_model=list[RecommendationView])
async def list_recommendations(user: RequireAuth, db: DbSession) -> list[RecommendationView]:
    rows = await recommender.list_pending(db, user)
    return [RecommendationView.model_validate(r) for r in rows]


@router.post("/recommendations/generate", response_model=list[RecommendationView])
async def generate_now(user: RequireAuth, db: DbSession) -> list[RecommendationView]:
    rows = await recommender.generate_recommendations(db, user)
    return [RecommendationView.model_validate(r) for r in rows]


@router.post("/recommendations/{rec_id}/accept", response_model=RecommendationView)
async def accept_rec(user: RequireAuth, db: DbSession, rec_id: uuid.UUID) -> RecommendationView:
    try:
        row = await auto_action.accept_recommendation(db, user, rec_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found") from None
    return RecommendationView.model_validate(row)


@router.post("/recommendations/{rec_id}/reject", response_model=RecommendationView)
async def reject_rec(user: RequireAuth, db: DbSession, rec_id: uuid.UUID) -> RecommendationView:
    try:
        row = await auto_action.reject_recommendation(db, user, rec_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found") from None
    return RecommendationView.model_validate(row)


@router.get("/policies", response_model=list[PolicyView])
async def list_policies(user: RequireAuth, db: DbSession) -> list[PolicyView]:
    rows = await db.scalars(select(AutoActionPolicy).where(AutoActionPolicy.tenant_id == user.tenant_id))
    return [PolicyView.model_validate(r) for r in rows.all()]


@router.post("/policies", response_model=PolicyView, status_code=201)
async def create_policy(user: RequireAuth, db: DbSession, payload: PolicyCreate) -> PolicyView:
    row = AutoActionPolicy(
        tenant_id=user.tenant_id,
        trigger_type=payload.trigger_type,
        min_confidence=payload.min_confidence,
        auto_apply=payload.auto_apply,
        approval_required=payload.approval_required,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return PolicyView.model_validate(row)


@router.get("/outcomes/summary")
async def outcomes_summary(user: RequireAuth, db: DbSession) -> dict[str, float]:
    return await outcome_tracker.success_rate(db, user)


@router.post("/recommendations/{rec_id}/outcome")
async def post_outcome(user: RequireAuth, db: DbSession, rec_id: uuid.UUID, body: JsonObject) -> RecommendationView:
    try:
        row = await outcome_tracker.record_outcome(db, user, rec_id, body)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found") from None
    return RecommendationView.model_validate(row)
