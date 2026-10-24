"""Mesh workflow CRUD and execution queries."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import cast

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.mesh.schemas import GeoLocation, MeshContext, MeshEvent
from app.mesh.workflow_executor import get_mesh_workflow_executor
from app.mesh.workflow_registry import definition_from_row, reload_workflows
from app.mesh.workflow_schema import (
    MeshWorkflowDefinition,
    MeshWorkflowRecordView,
    WorkflowDryRunResponse,
    WorkflowExecutionResult,
    WorkflowExecutionStatus,
)
from app.models.mesh_workflow import MeshWorkflow, MeshWorkflowExecution
from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient


def _to_view(row: MeshWorkflow) -> MeshWorkflowRecordView:
    return MeshWorkflowRecordView(
        id=row.id,
        tenant_id=row.tenant_id,
        name=row.name,
        description=row.description,
        enabled=row.enabled,
        definition=definition_from_row(row),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _execution_view(row: MeshWorkflowExecution) -> WorkflowExecutionResult:
    return WorkflowExecutionResult(
        id=row.id,
        workflow_id=row.workflow_id,
        tenant_id=row.tenant_id,
        trigger_event_id=row.trigger_event_id,
        status=WorkflowExecutionStatus(row.status),
        started_at=row.started_at,
        completed_at=row.completed_at,
        duration_ms=row.duration_ms,
        action_results=cast(JsonObject, row.action_results) if isinstance(row.action_results, dict) else {},
        error_message=row.error_message,
        correlation_id=row.correlation_id,
    )


async def create_workflow(
    db: AsyncSession,
    redis: RedisClient,
    user: CurrentUser,
    definition: MeshWorkflowDefinition,
) -> MeshWorkflowRecordView:
    row = MeshWorkflow(
        tenant_id=user.tenant_id,
        name=definition.name,
        description=definition.description,
        enabled=definition.enabled,
        definition={
            "trigger": definition.trigger.model_dump(mode="json"),
            "conditions": [item.model_dump(mode="json") for item in definition.conditions],
            "actions": [item.model_dump(mode="json") for item in definition.actions],
        },
    )
    db.add(row)
    await db.flush()
    await reload_workflows(db, user.tenant_id)
    return _to_view(row)


async def list_workflows(
    db: AsyncSession,
    user: CurrentUser,
    enabled: bool | None,
) -> list[MeshWorkflowRecordView]:
    query = select(MeshWorkflow).where(MeshWorkflow.tenant_id == user.tenant_id)
    if enabled is not None:
        query = query.where(MeshWorkflow.enabled.is_(enabled))
    rows = await db.scalars(query.order_by(MeshWorkflow.created_at.desc()))
    return [_to_view(row) for row in rows.all()]


async def get_workflow(db: AsyncSession, user: CurrentUser, workflow_id: uuid.UUID) -> MeshWorkflowRecordView:
    row = await db.scalar(select(MeshWorkflow).where(MeshWorkflow.id == workflow_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if not user.is_super_admin and row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return _to_view(row)


async def update_workflow(
    db: AsyncSession,
    redis: RedisClient,
    user: CurrentUser,
    workflow_id: uuid.UUID,
    definition: MeshWorkflowDefinition,
) -> MeshWorkflowRecordView:
    row = await db.scalar(select(MeshWorkflow).where(MeshWorkflow.id == workflow_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if not user.is_super_admin and row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    row.name = definition.name
    row.description = definition.description
    row.enabled = definition.enabled
    row.definition = {
        "trigger": definition.trigger.model_dump(mode="json"),
        "conditions": [item.model_dump(mode="json") for item in definition.conditions],
        "actions": [item.model_dump(mode="json") for item in definition.actions],
    }
    await db.flush()
    await reload_workflows(db, row.tenant_id)
    return _to_view(row)


async def delete_workflow(
    db: AsyncSession,
    redis: RedisClient,
    user: CurrentUser,
    workflow_id: uuid.UUID,
) -> None:
    row = await db.scalar(select(MeshWorkflow).where(MeshWorkflow.id == workflow_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if not user.is_super_admin and row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    tenant_id = row.tenant_id
    await db.delete(row)
    await db.flush()
    await reload_workflows(db, tenant_id)


def _sample_event_from_payload(user: CurrentUser, payload: JsonObject) -> MeshEvent:
    from datetime import UTC, datetime

    from app.mesh.event_bus import MeshDomain

    geo_raw = payload.get("geo_location")
    geo: GeoLocation | None = None
    if isinstance(geo_raw, dict):
        lat = geo_raw.get("lat")
        lng = geo_raw.get("lng")
        if isinstance(lat, int | float) and isinstance(lng, int | float):
            geo = GeoLocation(lat=float(lat), lng=float(lng))
    farm_raw = payload.get("farm_id")
    plot_raw = payload.get("plot_id")
    zone_raw = payload.get("physical_zone")
    physical_zone = zone_raw if isinstance(zone_raw, str) else None
    context = MeshContext(
        farm_id=uuid.UUID(str(farm_raw)) if isinstance(farm_raw, str) else None,
        plot_id=uuid.UUID(str(plot_raw)) if isinstance(plot_raw, str) else None,
        geo_location=geo,
        physical_zone=physical_zone,
        capabilities=[],
    )
    device_raw = payload.get("device_id")
    payload_body = payload.get("payload")
    event_payload: JsonObject = payload_body if isinstance(payload_body, dict) else {}
    return MeshEvent(
        event_id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        device_id=uuid.UUID(str(device_raw)) if device_raw is not None else uuid.uuid4(),
        domain=MeshDomain(str(payload.get("domain", "sensor"))),
        event_type=str(payload.get("event_type", "reading_update")),
        timestamp=datetime.now(tz=UTC),
        payload=event_payload,
        context=context,
    )


async def dry_run_workflow(
    db: AsyncSession,
    user: CurrentUser,
    workflow_id: uuid.UUID,
    sample: JsonObject,
) -> WorkflowDryRunResponse:
    row = await db.scalar(select(MeshWorkflow).where(MeshWorkflow.id == workflow_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if not user.is_super_admin and row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    executor = get_mesh_workflow_executor()
    if executor is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Workflow executor unavailable")
    definition = definition_from_row(row)
    event = _sample_event_from_payload(user, sample)
    template_context = executor.build_template_context(event, {})
    conditions_passed = await executor.evaluate_conditions(db, row.tenant_id, definition, template_context)
    if not conditions_passed:
        return WorkflowDryRunResponse(
            conditions_passed=False,
            planned_actions=[],
            skipped_reason="conditions_failed",
        )
    planned = await executor.plan_actions(db, row.tenant_id, definition, template_context)
    return WorkflowDryRunResponse(conditions_passed=True, planned_actions=planned, skipped_reason=None)


async def execute_workflow_manual(
    db: AsyncSession,
    user: CurrentUser,
    workflow_id: uuid.UUID,
    sample: JsonObject,
) -> WorkflowExecutionResult:
    row = await db.scalar(select(MeshWorkflow).where(MeshWorkflow.id == workflow_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if not user.is_super_admin and row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    executor = get_mesh_workflow_executor()
    if executor is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Workflow executor unavailable")
    definition = definition_from_row(row)
    event = _sample_event_from_payload(user, sample)
    execution = await executor.execute(
        db,
        workflow_id=row.id,
        tenant_id=row.tenant_id,
        definition=definition,
        trigger_event=event,
        dry_run=False,
    )
    return _execution_view(execution)


async def list_workflow_executions(
    db: AsyncSession,
    user: CurrentUser,
    workflow_id: uuid.UUID,
    status_filter: WorkflowExecutionStatus | None,
    since: datetime | None,
    until: datetime | None,
    limit: int,
) -> list[WorkflowExecutionResult]:
    await get_workflow(db, user, workflow_id)
    query = (
        select(MeshWorkflowExecution)
        .where(MeshWorkflowExecution.workflow_id == workflow_id)
        .order_by(MeshWorkflowExecution.started_at.desc())
        .limit(limit)
    )
    if not user.is_super_admin:
        query = query.where(MeshWorkflowExecution.tenant_id == user.tenant_id)
    if status_filter is not None:
        query = query.where(MeshWorkflowExecution.status == status_filter.value)
    if since is not None:
        query = query.where(MeshWorkflowExecution.started_at >= since)
    if until is not None:
        query = query.where(MeshWorkflowExecution.started_at <= until)
    rows = await db.scalars(query)
    return [_execution_view(row) for row in rows.all()]


async def get_workflow_execution(
    db: AsyncSession,
    user: CurrentUser,
    execution_id: uuid.UUID,
) -> WorkflowExecutionResult:
    row = await db.scalar(select(MeshWorkflowExecution).where(MeshWorkflowExecution.id == execution_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")
    if not user.is_super_admin and row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return _execution_view(row)
