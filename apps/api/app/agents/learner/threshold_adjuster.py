"""Suggest threshold adjustments from fire/success patterns."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.models import AgentThresholdAdjustment, ThresholdAdjustmentStatus
from app.models.mesh_workflow import MeshWorkflowExecution


@dataclass(frozen=True)
class ThresholdAdjustment:
    workflow_id: uuid.UUID
    metric: str
    old_value: float
    suggested_value: float
    reason: str


class ThresholdAdjuster:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def analyze_and_adjust(self, workflow_id: uuid.UUID, period_days: int = 30) -> ThresholdAdjustment | None:
        rows = await self._db.execute(
            select(
                func.count().label("total"),
                func.sum(case((MeshWorkflowExecution.status == "success", 1), else_=0)).label("ok"),
            ).where(MeshWorkflowExecution.workflow_id == workflow_id)
        )
        total, ok = rows.one()
        total_i = int(total or 0)
        ok_i = int(ok or 0)
        if total_i < 20:
            return None

        success_rate = ok_i / total_i
        fires_per_day = total_i / max(period_days, 1)
        old_value = 40.0
        suggested = old_value
        reason = "Within expected range"

        if fires_per_day > 50 and success_rate < 0.35:
            suggested = 35.0
            reason = (
                "Rule fires too often with low success — suggest lower threshold from 40 to 35"
            )
        elif fires_per_day < 2 and success_rate > 0.8:
            suggested = 42.0
            reason = "Rule rarely fires with high success — consider slightly higher threshold"

        if suggested == old_value:
            return None

        return ThresholdAdjustment(
            workflow_id=workflow_id,
            metric="soil_moisture_percent",
            old_value=old_value,
            suggested_value=suggested,
            reason=reason,
        )

    async def persist_suggestion(
        self,
        tenant_id: uuid.UUID,
        adjustment: ThresholdAdjustment,
    ) -> AgentThresholdAdjustment:
        row = AgentThresholdAdjustment(
            workflow_id=adjustment.workflow_id,
            tenant_id=tenant_id,
            metric=adjustment.metric,
            old_value=adjustment.old_value,
            suggested_value=adjustment.suggested_value,
            reason=adjustment.reason,
            status=ThresholdAdjustmentStatus.PENDING,
        )
        self._db.add(row)
        await self._db.flush()
        return row
