"""Aggregate mesh workflow execution metrics."""

from __future__ import annotations

import uuid
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from typing import cast

from fastapi import HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.mesh.workflow_schema import WorkflowExecutionStatus
from app.models.mesh_workflow import MeshWorkflow, MeshWorkflowExecution
from app.types.json_types import JsonObject
from app.workflows.analytics.schemas import (
    FailureReportView,
    SavingsReportView,
    TimelineDataView,
    TimelinePointView,
    WorkflowStatsView,
)


def _estimate_savings_from_definition(definition: JsonObject) -> tuple[float, float, float]:
    water_liters = 0.0
    kwh = 0.0
    actions = definition.get("actions")
    if not isinstance(actions, list):
        return water_liters, kwh, water_liters * 50.0 + kwh * 1500.0
    for action in actions:
        if not isinstance(action, dict):
            continue
        action_type = action.get("type")
        duration_raw = action.get("duration_minutes")
        minutes = float(duration_raw) if isinstance(duration_raw, int | float) else 0.0
        if action_type == "set_actuator":
            water_liters += (minutes / 15.0) * 37.0
        if action_type in {"set_actuator", "dispatch_device"}:
            channel = action.get("channels")
            if channel == "lighting" or action.get("action") == "lights_off":
                kwh += (minutes / 60.0) * 0.5
    idr = water_liters * 50.0 + kwh * 1500.0
    return water_liters, kwh, idr


class WorkflowAnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _workflow_for_user(self, workflow_id: uuid.UUID, user: CurrentUser) -> MeshWorkflow:
        row = await self._db.scalar(select(MeshWorkflow).where(MeshWorkflow.id == workflow_id))
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
        if not user.is_super_admin and row.tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return row

    async def top_fired_workflows(
        self,
        tenant_id: uuid.UUID,
        period_days: int,
        limit: int,
    ) -> list[WorkflowStatsView]:
        since = datetime.now(tz=UTC) - timedelta(days=period_days)
        rows = await self._db.execute(
            select(
                MeshWorkflowExecution.workflow_id,
                MeshWorkflow.name,
                func.count().label("fire_count"),
                func.sum(
                    case(
                        (MeshWorkflowExecution.status == WorkflowExecutionStatus.SUCCESS.value, 1),
                        else_=0,
                    )
                ).label("success_count"),
                func.sum(
                    case(
                        (MeshWorkflowExecution.status == WorkflowExecutionStatus.FAILED.value, 1),
                        else_=0,
                    )
                ).label("fail_count"),
                func.avg(MeshWorkflowExecution.duration_ms).label("avg_duration_ms"),
            )
            .join(MeshWorkflow, MeshWorkflow.id == MeshWorkflowExecution.workflow_id)
            .where(
                MeshWorkflowExecution.tenant_id == tenant_id,
                MeshWorkflowExecution.started_at >= since,
            )
            .group_by(MeshWorkflowExecution.workflow_id, MeshWorkflow.name)
            .order_by(func.count().desc())
            .limit(limit)
        )
        stats: list[WorkflowStatsView] = []
        for row in rows:
            workflow_id = row.workflow_id
            mesh = await self._db.get(MeshWorkflow, workflow_id)
            definition = cast(JsonObject, mesh.definition) if mesh and isinstance(mesh.definition, dict) else {}
            _, _, idr = _estimate_savings_from_definition(definition)
            fire_count = int(row.fire_count or 0)
            stats.append(
                WorkflowStatsView(
                    workflow_id=workflow_id,
                    name=str(row.name),
                    fire_count=fire_count,
                    success_count=int(row.success_count or 0),
                    fail_count=int(row.fail_count or 0),
                    avg_duration_ms=float(row.avg_duration_ms or 0.0),
                    savings_idr_estimate=idr * fire_count,
                )
            )
        return stats

    async def workflow_timeline(
        self,
        workflow_id: uuid.UUID,
        user: CurrentUser,
        period_days: int,
    ) -> TimelineDataView:
        await self._workflow_for_user(workflow_id, user)
        since = datetime.now(tz=UTC) - timedelta(days=period_days)
        rows = await self._db.execute(
            select(
                func.date_trunc("day", MeshWorkflowExecution.started_at).label("day"),
                func.count().label("fire_count"),
                func.sum(
                    case(
                        (MeshWorkflowExecution.status == WorkflowExecutionStatus.SUCCESS.value, 1),
                        else_=0,
                    )
                ).label("success_count"),
            )
            .where(
                MeshWorkflowExecution.workflow_id == workflow_id,
                MeshWorkflowExecution.started_at >= since,
            )
            .group_by("day")
            .order_by("day")
        )
        points: list[TimelinePointView] = []
        for row in rows:
            day_val = row.day
            if isinstance(day_val, datetime):
                points.append(
                    TimelinePointView(
                        date=day_val.date(),
                        fire_count=int(row.fire_count or 0),
                        success_count=int(row.success_count or 0),
                    )
                )
        return TimelineDataView(points=points)

    async def savings_per_workflow(self, workflow_id: uuid.UUID, user: CurrentUser) -> SavingsReportView:
        mesh = await self._workflow_for_user(workflow_id, user)
        definition = cast(JsonObject, mesh.definition) if isinstance(mesh.definition, dict) else {}
        water, kwh, idr = _estimate_savings_from_definition(definition)
        exec_count = await self._db.scalar(
            select(func.count())
            .select_from(MeshWorkflowExecution)
            .where(
                MeshWorkflowExecution.workflow_id == workflow_id,
                MeshWorkflowExecution.status == WorkflowExecutionStatus.SUCCESS.value,
            )
        )
        multiplier = int(exec_count or 0)
        breakdown: JsonObject = {
            "assumption_valve_15min_liters": 37.0,
            "assumption_light_1h_kwh": 0.5,
            "successful_executions": multiplier,
        }
        return SavingsReportView(
            water_liters_saved=water * multiplier,
            kwh_saved=kwh * multiplier,
            idr_total=idr * multiplier,
            calculation_breakdown=breakdown,
        )

    async def failure_analysis(self, workflow_id: uuid.UUID, user: CurrentUser) -> FailureReportView:
        await self._workflow_for_user(workflow_id, user)
        rows = await self._db.scalars(
            select(MeshWorkflowExecution).where(MeshWorkflowExecution.workflow_id == workflow_id)
        )
        executions = list(rows.all())
        total = len(executions)
        failed = [row for row in executions if row.status == WorkflowExecutionStatus.FAILED.value]
        errors = Counter(str(row.error_message or "unknown") for row in failed)
        common = [msg for msg, _ in errors.most_common(3)]
        failed_step = None
        if failed:
            results = failed[0].action_results if isinstance(failed[0].action_results, dict) else {}
            for key in results:
                failed_step = str(key)
                break
        rate = (len(failed) / total) if total else 0.0
        suggestion = "Review action device resolution and retry with dry-run."
        if common and "timeout" in common[0].lower():
            suggestion = "Increase action timeout or verify device online status."
        return FailureReportView(
            common_errors=common,
            failed_at_step=failed_step,
            suggested_fix=suggestion,
            failure_rate=rate,
        )
