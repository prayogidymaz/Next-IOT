"""CRUD service for tenant automation pipelines."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.automation.schemas import AutomationPipelineCreateRequest, AutomationPipelineUpdateRequest
from app.automation.xyflow_adapter import normalize_pipeline_payload
from app.models.automation_pipeline import AutomationPipeline


def _validate_pipeline_graph(nodes: list, edges: list) -> None:
    from app.rules.pipeline_validation import validate_pipeline_document

    errors, _warnings = validate_pipeline_document(nodes, edges)
    if errors:
        raise ValueError("; ".join(errors))


def _serialize_pipeline(pipeline: AutomationPipeline) -> dict[str, JsonValue]:
    return {
        "id": pipeline.id,
        "tenant_id": pipeline.tenant_id,
        "name": pipeline.name,
        "description": pipeline.description,
        "is_active": pipeline.is_active,
        "nodes_json": pipeline.nodes_json or [],
        "edges_json": pipeline.edges_json or [],
        "created_at": pipeline.created_at,
        "updated_at": pipeline.updated_at,
    }


class AutomationPipelineService:
    async def list_pipelines(self, db: AsyncSession, user: CurrentUser) -> list[dict[str, JsonValue]]:
        query = (
            select(AutomationPipeline)
            .where(AutomationPipeline.tenant_id == user.tenant_id)
            .order_by(AutomationPipeline.name)
        )
        rows = (await db.scalars(query)).all()
        return [_serialize_pipeline(row) for row in rows]

    async def get_pipeline(
        self,
        db: AsyncSession,
        user: CurrentUser,
        pipeline_id: uuid.UUID,
    ) -> dict[str, JsonValue]:
        pipeline = await self._get_pipeline_for_user(db, user, pipeline_id)
        return _serialize_pipeline(pipeline)

    async def create_pipeline(
        self,
        db: AsyncSession,
        user: CurrentUser,
        payload: AutomationPipelineCreateRequest,
    ) -> dict[str, JsonValue]:
        nodes_json, edges_json = normalize_pipeline_payload(payload.nodes_json, payload.edges_json)
        _validate_pipeline_graph(nodes_json, edges_json)
        pipeline = AutomationPipeline(
            tenant_id=user.tenant_id,
            name=payload.name.strip(),
            description=payload.description,
            is_active=payload.is_active,
            nodes_json=nodes_json,
            edges_json=edges_json,
        )
        db.add(pipeline)
        await db.flush()
        await db.refresh(pipeline)
        return _serialize_pipeline(pipeline)

    async def update_pipeline(
        self,
        db: AsyncSession,
        user: CurrentUser,
        pipeline_id: uuid.UUID,
        payload: AutomationPipelineUpdateRequest,
    ) -> dict[str, JsonValue]:
        pipeline = await self._get_pipeline_for_user(db, user, pipeline_id)

        if payload.name is not None:
            pipeline.name = payload.name.strip()
        if payload.description is not None:
            pipeline.description = payload.description
        if payload.is_active is not None:
            pipeline.is_active = payload.is_active
        if payload.nodes_json is not None or payload.edges_json is not None:
            nodes = payload.nodes_json if payload.nodes_json is not None else (pipeline.nodes_json or [])
            edges = payload.edges_json if payload.edges_json is not None else (pipeline.edges_json or [])
            nodes, edges = normalize_pipeline_payload(nodes, edges)
            pipeline.nodes_json = nodes
            pipeline.edges_json = edges

        _validate_pipeline_graph(pipeline.nodes_json or [], pipeline.edges_json or [])
        pipeline.updated_at = datetime.now(UTC)
        await db.flush()
        await db.refresh(pipeline)
        return _serialize_pipeline(pipeline)

    async def delete_pipeline(
        self,
        db: AsyncSession,
        user: CurrentUser,
        pipeline_id: uuid.UUID,
    ) -> None:
        pipeline = await self._get_pipeline_for_user(db, user, pipeline_id)
        await db.delete(pipeline)
        await db.flush()

    async def _get_pipeline_for_user(
        self,
        db: AsyncSession,
        user: CurrentUser,
        pipeline_id: uuid.UUID,
    ) -> AutomationPipeline:
        query = select(AutomationPipeline).where(
            AutomationPipeline.id == pipeline_id,
            AutomationPipeline.tenant_id == user.tenant_id,
        )
        pipeline = await db.scalar(query)
        if pipeline is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation pipeline not found")
        return pipeline


automation_pipeline_service = AutomationPipelineService()
