"""Mesh workflow HTTP API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.auth.dependencies import RequireAuth
from app.deps import DbSession, RedisDep
from app.mesh.workflow_schema import (
    MeshWorkflowDefinition,
    MeshWorkflowRecordView,
    WorkflowDryRunRequest,
    WorkflowDryRunResponse,
    WorkflowExecutionResult,
    WorkflowExecutionStatus,
)
from app.mesh.workflow_service import (
    create_workflow,
    delete_workflow,
    dry_run_workflow,
    execute_workflow_manual,
    get_workflow,
    get_workflow_execution,
    list_workflow_executions,
    list_workflows,
    update_workflow,
)

WorkflowStatusQuery = Annotated[WorkflowExecutionStatus | None, Query(alias="status")]

router = APIRouter(prefix="/api/v1/mesh", tags=["mesh-workflows"])


@router.post("/workflows", response_model=MeshWorkflowRecordView, status_code=status.HTTP_201_CREATED)
async def post_workflow(
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
    payload: MeshWorkflowDefinition,
) -> MeshWorkflowRecordView:
    return await create_workflow(db, redis, user, payload)


@router.get("/workflows", response_model=list[MeshWorkflowRecordView])
async def get_workflows(
    user: RequireAuth,
    db: DbSession,
    enabled: bool | None = None,
) -> list[MeshWorkflowRecordView]:
    return await list_workflows(db, user, enabled)


@router.get("/workflows/{workflow_id}", response_model=MeshWorkflowRecordView)
async def get_workflow_detail(user: RequireAuth, db: DbSession, workflow_id: uuid.UUID) -> MeshWorkflowRecordView:
    return await get_workflow(db, user, workflow_id)


@router.patch("/workflows/{workflow_id}", response_model=MeshWorkflowRecordView)
async def patch_workflow(
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
    workflow_id: uuid.UUID,
    payload: MeshWorkflowDefinition,
) -> MeshWorkflowRecordView:
    return await update_workflow(db, redis, user, workflow_id, payload)


@router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def remove_workflow(
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
    workflow_id: uuid.UUID,
) -> Response:
    await delete_workflow(db, redis, user, workflow_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/workflows/{workflow_id}/test", response_model=WorkflowDryRunResponse)
async def test_workflow(
    user: RequireAuth,
    db: DbSession,
    workflow_id: uuid.UUID,
    payload: WorkflowDryRunRequest,
) -> WorkflowDryRunResponse:
    return await dry_run_workflow(db, user, workflow_id, payload.sample_event)


@router.post("/workflows/{workflow_id}/execute", response_model=WorkflowExecutionResult)
async def execute_workflow(
    user: RequireAuth,
    db: DbSession,
    workflow_id: uuid.UUID,
    payload: WorkflowDryRunRequest,
) -> WorkflowExecutionResult:
    return await execute_workflow_manual(db, user, workflow_id, payload.sample_event)


@router.get("/workflows/{workflow_id}/executions", response_model=list[WorkflowExecutionResult])
async def get_workflow_executions(
    user: RequireAuth,
    db: DbSession,
    workflow_id: uuid.UUID,
    status_filter: WorkflowStatusQuery = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[WorkflowExecutionResult]:
    return await list_workflow_executions(db, user, workflow_id, status_filter, since, until, limit)


@router.get("/workflow-executions/{execution_id}", response_model=WorkflowExecutionResult)
async def get_execution_detail(
    user: RequireAuth,
    db: DbSession,
    execution_id: uuid.UUID,
) -> WorkflowExecutionResult:
    return await get_workflow_execution(db, user, execution_id)
