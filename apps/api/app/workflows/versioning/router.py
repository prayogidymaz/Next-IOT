"""Workflow versioning HTTP routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.mesh.workflow_service import get_workflow
from app.mesh.workflow_schema import MeshWorkflowRecordView
from app.workflows.versioning.schemas import CreateVersionBody, VersionDiffView, WorkflowVersionView
from app.workflows.versioning.service import VersioningService, _to_view

router = APIRouter(prefix="/api/v1/workflows", tags=["workflow-versioning"])


@router.get("/{workflow_id}/versions", response_model=list[WorkflowVersionView])
async def list_workflow_versions(
    user: RequireAuth,
    db: DbSession,
    workflow_id: uuid.UUID,
) -> list[WorkflowVersionView]:
    service = VersioningService(db)
    rows = await service.list_versions(workflow_id, user)
    return [_to_view(row) for row in rows]


@router.post("/{workflow_id}/versions", response_model=WorkflowVersionView, status_code=201)
async def create_workflow_version(
    user: RequireAuth,
    db: DbSession,
    workflow_id: uuid.UUID,
    body: CreateVersionBody,
) -> WorkflowVersionView:
    _ = body.notes
    mesh = await get_workflow(db, user, workflow_id)
    service = VersioningService(db)
    snapshot = {
        "name": mesh.name,
        "description": mesh.description,
        "enabled": mesh.enabled,
        "definition": mesh.definition.model_dump(mode="json"),
    }
    row = await service.create_version(workflow_id, snapshot, user.user_id)
    return _to_view(row)


@router.post("/{workflow_id}/versions/{version_number}/rollback", response_model=MeshWorkflowRecordView)
async def rollback_workflow_version(
    user: RequireAuth,
    db: DbSession,
    workflow_id: uuid.UUID,
    version_number: int,
) -> MeshWorkflowRecordView:
    service = VersioningService(db)
    mesh = await service.rollback_to(workflow_id, version_number, user)
    return await get_workflow(db, user, mesh.id)


@router.get("/{workflow_id}/versions/{version_a}/diff/{version_b}", response_model=VersionDiffView)
async def diff_workflow_versions(
    user: RequireAuth,
    db: DbSession,
    workflow_id: uuid.UUID,
    version_a: uuid.UUID,
    version_b: uuid.UUID,
) -> VersionDiffView:
    _ = workflow_id
    service = VersioningService(db)
    return await service.diff(version_a, version_b, user)
