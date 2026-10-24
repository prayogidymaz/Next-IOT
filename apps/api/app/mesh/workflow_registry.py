"""In-memory cache of enabled mesh workflows (hot reload)."""

from __future__ import annotations

import logging
import uuid
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mesh.schemas import MeshEvent
from app.mesh.workflow_matching import workflow_matches_event
from app.mesh.workflow_schema import MeshWorkflowDefinition
from app.models.mesh_workflow import MeshWorkflow

logger = logging.getLogger(__name__)

_CacheEntry = tuple[uuid.UUID, MeshWorkflowDefinition]


def definition_from_row(row: MeshWorkflow) -> MeshWorkflowDefinition:
    raw = row.definition if isinstance(row.definition, dict) else {}
    from app.types.json_types import JsonObject

    merged: JsonObject = {
        "name": row.name,
        "description": row.description,
        "enabled": row.enabled,
        **cast(JsonObject, raw),
    }
    return MeshWorkflowDefinition.model_validate(merged)

_tenant_workflows: dict[uuid.UUID, list[_CacheEntry]] = {}


async def reload_workflows(db: AsyncSession, tenant_id: uuid.UUID | None = None) -> None:
    global _tenant_workflows
    query = select(MeshWorkflow).where(MeshWorkflow.enabled.is_(True))
    if tenant_id is not None:
        query = query.where(MeshWorkflow.tenant_id == tenant_id)
    rows = await db.scalars(query)
    if tenant_id is not None:
        entries: list[_CacheEntry] = []
        for row in rows.all():
            definition = definition_from_row(row)
            entries.append((row.id, definition))
        _tenant_workflows[tenant_id] = entries
        return
    rebuilt: dict[uuid.UUID, list[_CacheEntry]] = {}
    for row in rows.all():
        definition = definition_from_row(row)
        rebuilt.setdefault(row.tenant_id, []).append((row.id, definition))
    _tenant_workflows = rebuilt
    logger.info("Mesh workflow registry reloaded tenants=%s", len(_tenant_workflows))


def matching_workflows(event: MeshEvent) -> list[tuple[uuid.UUID, MeshWorkflowDefinition]]:
    entries = _tenant_workflows.get(event.tenant_id, [])
    matched: list[tuple[uuid.UUID, MeshWorkflowDefinition]] = []
    for workflow_id, definition in entries:
        if workflow_matches_event(definition, event):
            matched.append((workflow_id, definition))
    return matched
