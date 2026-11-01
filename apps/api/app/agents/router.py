"""Agent operations HTTP routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status

from app.agents.schemas import (
    AlertClusterView,
    BatchExecuteBody,
    ChainExecutionView,
    HealingSuggestionView,
    ThresholdSuggestionView,
    TriggerChainBody,
)
from app.agents.service import AgentOperationsService
from app.auth.dependencies import RequireAuth
from app.deps import DbSession, RedisDep

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


def _healing_view(row: object) -> HealingSuggestionView:
    from app.agents.models import AgentHealingSuggestion

    assert isinstance(row, AgentHealingSuggestion)
    return HealingSuggestionView(
        id=row.id,
        workflow_id=row.workflow_id,
        diagnosis_json=row.diagnosis_json if isinstance(row.diagnosis_json, dict) else {},
        fix_json=row.fix_json if isinstance(row.fix_json, dict) else {},
        confidence=row.confidence,
        status=row.status,
        created_at=row.created_at,
    )


@router.get("/healing/suggestions", response_model=list[HealingSuggestionView])
async def list_healing_suggestions(user: RequireAuth, db: DbSession, redis: RedisDep) -> list[HealingSuggestionView]:
    service = AgentOperationsService(db, redis)
    await service.scan_and_create_healing(user)
    rows = await service.list_healing_suggestions(user)
    return [_healing_view(r) for r in rows]


@router.post("/healing/{suggestion_id}/approve", response_model=HealingSuggestionView)
async def approve_healing(
    suggestion_id: uuid.UUID,
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
) -> HealingSuggestionView:
    row = await AgentOperationsService(db, redis).approve_healing(suggestion_id, user)
    return _healing_view(row)


@router.post("/healing/{suggestion_id}/reject", response_model=HealingSuggestionView)
async def reject_healing(
    suggestion_id: uuid.UUID,
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
) -> HealingSuggestionView:
    row = await AgentOperationsService(db, redis).reject_healing(suggestion_id, user)
    return _healing_view(row)


@router.get("/chains/active", response_model=list[ChainExecutionView])
async def list_active_chains(user: RequireAuth, db: DbSession, redis: RedisDep) -> list[ChainExecutionView]:
    rows = await AgentOperationsService(db, redis).list_active_chains(user)
    return [
        ChainExecutionView(
            id=r.id,
            chain_id=r.chain_id,
            tenant_id=r.tenant_id,
            current_step=r.current_step,
            status=r.status,
            started_at=r.started_at,
            completed_at=r.completed_at,
        )
        for r in rows
    ]


@router.post("/chains/{chain_name}/trigger", response_model=ChainExecutionView, status_code=201)
async def trigger_chain(
    chain_name: str,
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
    body: TriggerChainBody,
) -> ChainExecutionView:
    row = await AgentOperationsService(db, redis).trigger_chain(chain_name, user, body.device_id)
    return ChainExecutionView(
        id=row.id,
        chain_id=row.chain_id,
        tenant_id=row.tenant_id,
        current_step=row.current_step,
        status=row.status,
        started_at=row.started_at,
        completed_at=row.completed_at,
    )


@router.get("/triage/clusters", response_model=list[AlertClusterView])
async def list_triage_clusters(user: RequireAuth, db: DbSession, redis: RedisDep) -> list[AlertClusterView]:
    rows = await AgentOperationsService(db, redis).list_clusters(user)
    return [
        AlertClusterView(
            id=r.id,
            cluster_signature=r.cluster_signature,
            alert_ids_json=r.alert_ids_json if isinstance(r.alert_ids_json, list) else [],
            risk_score=r.risk_score,
            suggested_action=r.suggested_action,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/triage/clusters/{cluster_id}/batch-execute", response_model=AlertClusterView)
async def batch_execute_cluster(
    cluster_id: uuid.UUID,
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
    body: BatchExecuteBody,
) -> AlertClusterView:
    if not body.approve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Batch execution requires approve=true")
    row = await AgentOperationsService(db, redis).batch_execute_cluster(cluster_id, user)
    return AlertClusterView(
        id=row.id,
        cluster_signature=row.cluster_signature,
        alert_ids_json=row.alert_ids_json if isinstance(row.alert_ids_json, list) else [],
        risk_score=row.risk_score,
        suggested_action=row.suggested_action,
        created_at=row.created_at,
    )


@router.get("/learning/suggestions", response_model=list[ThresholdSuggestionView])
async def list_learning_suggestions(
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
) -> list[ThresholdSuggestionView]:
    rows = await AgentOperationsService(db, redis).list_learning_suggestions(user)
    return [
        ThresholdSuggestionView(
            id=r.id,
            workflow_id=r.workflow_id,
            metric=r.metric,
            old_value=r.old_value,
            suggested_value=r.suggested_value,
            reason=r.reason,
            status=r.status,
        )
        for r in rows
    ]


@router.post("/learning/{suggestion_id}/apply", response_model=ThresholdSuggestionView)
async def apply_learning_suggestion(
    suggestion_id: uuid.UUID,
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
) -> ThresholdSuggestionView:
    row = await AgentOperationsService(db, redis).apply_learning(suggestion_id, user)
    return ThresholdSuggestionView(
        id=row.id,
        workflow_id=row.workflow_id,
        metric=row.metric,
        old_value=row.old_value,
        suggested_value=row.suggested_value,
        reason=row.reason,
        status=row.status,
    )
