"""Facade for agent operations used by HTTP router."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.healer.workflow_healer import WorkflowHealer
from app.agents.learner.threshold_adjuster import ThresholdAdjuster
from app.agents.models import (
    AgentAlertCluster,
    AgentChainExecution,
    AgentHealingSuggestion,
    AgentThresholdAdjustment,
    ChainExecutionStatus,
    HealingSuggestionStatus,
    ThresholdAdjustmentStatus,
)
from app.agents.responder.chain_executor import ChainExecutor
from app.agents.triage.alert_clusterer import AlertClusterer
from app.agents.triage.batch_action import BatchAction
from app.agents.triage.risk_scorer import RiskScorer
from app.agents.responder.chain_definitions import CHAIN_REGISTRY
from app.agents.triage.types import AlertCluster, AlertSnapshot
from app.auth.dependencies import CurrentUser
from app.models.alarm import Alarm
from app.types.redis_client import RedisClient


class AgentOperationsService:
    def __init__(self, db: AsyncSession, redis: RedisClient) -> None:
        self._db = db
        self._redis = redis
        self._healer = WorkflowHealer(db)
        self._clusterer = AlertClusterer()
        self._risk = RiskScorer()
        self._batch = BatchAction()
        self._thresholds = ThresholdAdjuster(db)

    async def list_healing_suggestions(self, user: CurrentUser) -> list[AgentHealingSuggestion]:
        rows = await self._db.scalars(
            select(AgentHealingSuggestion)
            .where(
                AgentHealingSuggestion.tenant_id == user.tenant_id,
                AgentHealingSuggestion.status == HealingSuggestionStatus.PENDING,
            )
            .order_by(AgentHealingSuggestion.created_at.desc())
        )
        return list(rows.all())

    async def approve_healing(self, suggestion_id: uuid.UUID, user: CurrentUser) -> AgentHealingSuggestion:
        row = await self._db.get(AgentHealingSuggestion, suggestion_id)
        if row is None or row.tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        await self._healer.apply_fix(suggestion_id, user)
        await self._db.refresh(row)
        return row

    async def reject_healing(self, suggestion_id: uuid.UUID, user: CurrentUser) -> AgentHealingSuggestion:
        row = await self._db.get(AgentHealingSuggestion, suggestion_id)
        if row is None or row.tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        row.status = HealingSuggestionStatus.REJECTED
        await self._db.flush()
        return row

    async def list_active_chains(self, user: CurrentUser) -> list[AgentChainExecution]:
        rows = await self._db.scalars(
            select(AgentChainExecution)
            .where(
                AgentChainExecution.tenant_id == user.tenant_id,
                AgentChainExecution.status.in_(
                    [ChainExecutionStatus.RUNNING, ChainExecutionStatus.PAUSED]
                ),
            )
            .order_by(AgentChainExecution.started_at.desc())
        )
        return list(rows.all())

    async def trigger_chain(self, chain_name: str, user: CurrentUser, device_id: uuid.UUID | None) -> AgentChainExecution:
        if chain_name not in CHAIN_REGISTRY:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown chain")
        executor = ChainExecutor(self._db, self._redis)
        row = await executor.start(
            chain_name,
            user.tenant_id,
            None,
            {"device_id": str(device_id) if device_id else None},
        )
        await executor.run_next_step(row.id)
        return row

    async def list_clusters(self, user: CurrentUser) -> list[AgentAlertCluster]:
        alarms = await self._db.scalars(
            select(Alarm).where(Alarm.tenant_id == user.tenant_id, Alarm.status == "active").limit(200)
        )
        snapshots: list[AlertSnapshot] = []
        for alarm in alarms.all():
            snapshots.append(
                AlertSnapshot(
                    id=alarm.id,
                    tenant_id=alarm.tenant_id,
                    alarm_type=alarm.alarm_type,
                    severity=str(alarm.severity),
                    title=alarm.title,
                    device_id=alarm.device_id,
                    lat=None,
                    lng=None,
                    metric=alarm.alarm_type,
                )
            )
        clusters = self._clusterer.cluster(snapshots)
        persisted: list[AgentAlertCluster] = []
        for cluster in clusters:
            score = self._risk.score(cluster.alerts[0], {}).value if cluster.alerts else 0
            cluster_view = AlertCluster(
                signature=cluster.signature,
                alerts=cluster.alerts,
                risk_score=float(score),
            )
            plan = self._batch.suggest_batch(cluster_view)
            row = AgentAlertCluster(
                tenant_id=user.tenant_id,
                cluster_signature=cluster.signature,
                alert_ids_json=[str(a.id) for a in cluster.alerts],
                risk_score=float(score),
                suggested_action=plan.summary,
            )
            self._db.add(row)
            persisted.append(row)
        await self._db.flush()
        return persisted

    async def batch_execute_cluster(self, cluster_id: uuid.UUID, user: CurrentUser) -> AgentAlertCluster:
        row = await self._db.get(AgentAlertCluster, cluster_id)
        if row is None or row.tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found")
        executor = ChainExecutor(self._db, self._redis)
        await executor.start("irrigation_smart", user.tenant_id, None, {"cluster_id": str(cluster_id)})
        row.resolved_at = datetime.now(tz=UTC)
        await self._db.flush()
        return row

    async def list_learning_suggestions(self, user: CurrentUser) -> list[AgentThresholdAdjustment]:
        rows = await self._db.scalars(
            select(AgentThresholdAdjustment)
            .where(
                AgentThresholdAdjustment.tenant_id == user.tenant_id,
                AgentThresholdAdjustment.status == ThresholdAdjustmentStatus.PENDING,
            )
            .order_by(AgentThresholdAdjustment.created_at.desc())
        )
        return list(rows.all())

    async def apply_learning(self, suggestion_id: uuid.UUID, user: CurrentUser) -> AgentThresholdAdjustment:
        row = await self._db.get(AgentThresholdAdjustment, suggestion_id)
        if row is None or row.tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        row.status = ThresholdAdjustmentStatus.APPLIED
        row.applied_at = datetime.now(tz=UTC)
        await self._db.flush()
        return row

    async def scan_and_create_healing(self, user: CurrentUser) -> list[AgentHealingSuggestion]:
        broken = await self._healer.detect_broken_workflows(user.tenant_id)
        created: list[AgentHealingSuggestion] = []
        for item in broken:
            diagnosis = await self._healer.diagnose(item.workflow_id)
            fix = await self._healer.suggest_fix(item.workflow_id, diagnosis)
            created.append(await self._healer.persist_suggestion(user.tenant_id, diagnosis, fix))
        return created
