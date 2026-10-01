"""Import / export automation pipelines via /api/v1/rules/* endpoints."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from pydantic import JsonValue
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.automation.pipeline_service import automation_pipeline_service
from app.automation.schemas import AutomationPipelineCreateRequest
from app.rules.pipeline_validation import validate_pipeline_document

EXPORT_SCHEMA_VERSION = "next-iot.automation-pipeline.v1"


def build_export_document(pipeline: dict[str, JsonValue]) -> dict[str, JsonValue]:
    return {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "exported_at": pipeline.get("updated_at"),
        "pipeline": {
            "id": str(pipeline["id"]),
            "name": pipeline["name"],
            "description": pipeline.get("description"),
            "is_active": pipeline.get("is_active", True),
            "nodes": pipeline.get("nodes_json") or [],
            "edges": pipeline.get("edges_json") or [],
        },
    }


async def export_pipeline_rule(
    db: AsyncSession,
    user: CurrentUser,
    pipeline_id: uuid.UUID,
) -> dict[str, JsonValue]:
    pipeline = await automation_pipeline_service.get_pipeline(db, user, pipeline_id)
    return build_export_document(pipeline)


async def import_pipeline_rule(
    db: AsyncSession,
    user: CurrentUser,
    document: dict[str, JsonValue],
) -> dict[str, JsonValue]:
    pipeline_body = document.get("pipeline") if "pipeline" in document else document
    if not isinstance(pipeline_body, dict):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid import document")

    nodes = pipeline_body.get("nodes") or pipeline_body.get("nodes_json") or []
    edges = pipeline_body.get("edges") or pipeline_body.get("edges_json") or []
    errors, _warnings = validate_pipeline_document(nodes, edges)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Pipeline validation failed", "errors": errors},
        )

    name = str(pipeline_body.get("name") or "Imported Pipeline").strip()
    payload = AutomationPipelineCreateRequest(
        name=name,
        description=pipeline_body.get("description"),
        is_active=bool(pipeline_body.get("is_active", True)),
        nodes_json=nodes,
        edges_json=edges,
    )
    try:
        created = await automation_pipeline_service.create_pipeline(db, user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return build_export_document(created)


def validate_pipeline_payload(document: dict[str, JsonValue]) -> dict[str, JsonValue]:
    pipeline_body = document.get("pipeline") if "pipeline" in document else document
    if not isinstance(pipeline_body, dict):
        return {"valid": False, "errors": ["document must contain a pipeline object"], "warnings": []}

    nodes = pipeline_body.get("nodes") or pipeline_body.get("nodes_json") or []
    edges = pipeline_body.get("edges") or pipeline_body.get("edges_json") or []
    node_list = nodes if isinstance(nodes, list) else []
    edge_list = edges if isinstance(edges, list) else []
    errors, warnings = validate_pipeline_document(node_list, edge_list)
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
