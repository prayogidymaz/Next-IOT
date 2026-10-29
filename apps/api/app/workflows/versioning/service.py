"""Workflow version CRUD, diff, and rollback."""

from __future__ import annotations

import uuid
from typing import cast

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.mesh.workflow_registry import reload_workflows
from app.models.mesh_workflow import MeshWorkflow
from app.types.json_types import JsonObject
from app.workflows.versioning.models import WorkflowVersion
from app.workflows.versioning.schemas import VersionDiffView, WorkflowVersionView


def _node_ids(snapshot: JsonObject) -> set[str]:
    ids: set[str] = set()
    actions = snapshot.get("actions")
    if isinstance(actions, list):
        for item in actions:
            if isinstance(item, dict):
                action_id = item.get("id")
                if isinstance(action_id, str):
                    ids.add(action_id)
    trigger = snapshot.get("trigger")
    if isinstance(trigger, dict):
        trigger_id = trigger.get("id")
        if isinstance(trigger_id, str):
            ids.add(trigger_id)
        else:
            ids.add("trigger")
    return ids


def _edge_keys(snapshot: JsonObject) -> set[str]:
    edges: set[str] = set()
    conditions = snapshot.get("conditions")
    if isinstance(conditions, list):
        for idx, item in enumerate(conditions):
            if isinstance(item, dict):
                edges.add(f"condition:{idx}:{item.get('id', idx)}")
    return edges


def _to_view(row: WorkflowVersion) -> WorkflowVersionView:
    snap = row.snapshot_json if isinstance(row.snapshot_json, dict) else {}
    return WorkflowVersionView(
        id=row.id,
        workflow_id=row.workflow_id,
        version_number=row.version_number,
        snapshot_json=cast(JsonObject, snap),
        created_by=row.created_by,
        created_at=row.created_at,
        is_active=row.is_active,
        parent_version_id=row.parent_version_id,
    )


class VersioningService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _get_workflow(self, workflow_id: uuid.UUID, user: CurrentUser) -> MeshWorkflow:
        row = await self._db.scalar(select(MeshWorkflow).where(MeshWorkflow.id == workflow_id))
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
        if not user.is_super_admin and row.tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return row

    async def create_version(
        self,
        workflow_id: uuid.UUID,
        snapshot_dict: JsonObject,
        user_id: uuid.UUID,
    ) -> WorkflowVersion:
        max_num = await self._db.scalar(
            select(func.coalesce(func.max(WorkflowVersion.version_number), 0)).where(
                WorkflowVersion.workflow_id == workflow_id
            )
        )
        next_num = int(max_num or 0) + 1
        active = await self.get_active_version(workflow_id)
        row = WorkflowVersion(
            workflow_id=workflow_id,
            version_number=next_num,
            snapshot_json=dict(snapshot_dict),
            created_by=user_id,
            is_active=False,
            parent_version_id=active.id if active is not None else None,
        )
        self._db.add(row)
        await self._db.flush()
        return row

    async def create_version_from_mesh_row(self, mesh_row: MeshWorkflow, user_id: uuid.UUID) -> WorkflowVersion:
        snapshot: JsonObject = {
            "name": mesh_row.name,
            "description": mesh_row.description,
            "enabled": mesh_row.enabled,
            "definition": cast(JsonObject, mesh_row.definition)
            if isinstance(mesh_row.definition, dict)
            else {},
        }
        return await self.create_version(mesh_row.id, snapshot, user_id)

    async def list_versions(self, workflow_id: uuid.UUID, user: CurrentUser) -> list[WorkflowVersion]:
        await self._get_workflow(workflow_id, user)
        rows = await self._db.scalars(
            select(WorkflowVersion)
            .where(WorkflowVersion.workflow_id == workflow_id)
            .order_by(WorkflowVersion.version_number.desc())
        )
        return list(rows.all())

    async def get_active_version(self, workflow_id: uuid.UUID) -> WorkflowVersion | None:
        return await self._db.scalar(
            select(WorkflowVersion).where(
                WorkflowVersion.workflow_id == workflow_id,
                WorkflowVersion.is_active.is_(True),
            )
        )

    async def rollback_to(
        self,
        workflow_id: uuid.UUID,
        version_number: int,
        user: CurrentUser,
    ) -> MeshWorkflow:
        mesh = await self._get_workflow(workflow_id, user)
        version = await self._db.scalar(
            select(WorkflowVersion).where(
                WorkflowVersion.workflow_id == workflow_id,
                WorkflowVersion.version_number == version_number,
            )
        )
        if version is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
        snap = version.snapshot_json if isinstance(version.snapshot_json, dict) else {}
        definition = snap.get("definition")
        if isinstance(definition, dict):
            mesh.definition = definition
        name_raw = snap.get("name")
        if isinstance(name_raw, str):
            mesh.name = name_raw
        desc_raw = snap.get("description")
        if isinstance(desc_raw, str):
            mesh.description = desc_raw
        enabled_raw = snap.get("enabled")
        if isinstance(enabled_raw, bool):
            mesh.enabled = enabled_raw
        await self._db.execute(
            update(WorkflowVersion)
            .where(WorkflowVersion.workflow_id == workflow_id)
            .values(is_active=False)
        )
        version.is_active = True
        await self._db.flush()
        await reload_workflows(self._db, mesh.tenant_id)
        return mesh

    async def diff(self, version_a_id: uuid.UUID, version_b_id: uuid.UUID, user: CurrentUser) -> VersionDiffView:
        version_a = await self._db.get(WorkflowVersion, version_a_id)
        version_b = await self._db.get(WorkflowVersion, version_b_id)
        if version_a is None or version_b is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
        if version_a.workflow_id != version_b.workflow_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Versions must belong to same workflow")
        await self._get_workflow(version_a.workflow_id, user)
        snap_a = version_a.snapshot_json if isinstance(version_a.snapshot_json, dict) else {}
        snap_b = version_b.snapshot_json if isinstance(version_b.snapshot_json, dict) else {}
        def_raw_a = snap_a.get("definition")
        def_raw_b = snap_b.get("definition")
        def_a = cast(JsonObject, def_raw_a) if isinstance(def_raw_a, dict) else {}
        def_b = cast(JsonObject, def_raw_b) if isinstance(def_raw_b, dict) else {}
        nodes_a = _node_ids(def_a)
        nodes_b = _node_ids(def_b)
        edges_a = _edge_keys(def_a)
        edges_b = _edge_keys(def_b)
        return VersionDiffView(
            added_nodes=sorted(nodes_b - nodes_a),
            removed_nodes=sorted(nodes_a - nodes_b),
            modified_nodes=sorted(nodes_a & nodes_b),
            added_edges=sorted(edges_b - edges_a),
            removed_edges=sorted(edges_a - edges_b),
        )
