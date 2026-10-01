import uuid

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RequireAutomationManage, RequireAutomationRun, RequireOperator
from app.automation.events import publish_pipeline_rules_updated
from app.automation.pipeline_interpreter import pipeline_interpreter_service
from app.automation.pipeline_service import automation_pipeline_service
from app.automation.schemas import (
    AutomationPipelineCreateRequest,
    AutomationPipelineListResponse,
    AutomationPipelineResponse,
    AutomationPipelineUpdateRequest,
    PipelineDryRunRequest,
    PipelineTestRunRequest,
    PipelineTestRunResponse,
)
from app.deps import get_db, get_redis
from app.models.automation_pipeline import AutomationPipeline
from app.rules.pipeline_validation import validate_pipeline_document

router = APIRouter(prefix="/api/v1/automation", tags=["automation"])


@router.get("/pipelines", response_model=AutomationPipelineListResponse)
async def list_pipelines(user: RequireOperator, db: AsyncSession = Depends(get_db)):
    items = await automation_pipeline_service.list_pipelines(db, user)
    return AutomationPipelineListResponse(
        count=len(items),
        items=[AutomationPipelineResponse.model_validate(item) for item in items],
    )


@router.get("/pipelines/{pipeline_id}", response_model=AutomationPipelineResponse)
async def get_pipeline(
    pipeline_id: uuid.UUID,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    item = await automation_pipeline_service.get_pipeline(db, user, pipeline_id)
    return AutomationPipelineResponse.model_validate(item)


@router.post("/pipelines", response_model=AutomationPipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    payload: AutomationPipelineCreateRequest,
    user: RequireAutomationManage,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    try:
        item = await automation_pipeline_service.create_pipeline(db, user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    await publish_pipeline_rules_updated(
        redis,
        tenant_id=str(user.tenant_id),
        pipeline_id=str(item["id"]),
        action="created",
        pipeline=item,
    )
    return AutomationPipelineResponse.model_validate(item)


@router.put("/pipelines/{pipeline_id}", response_model=AutomationPipelineResponse)
async def update_pipeline(
    pipeline_id: uuid.UUID,
    payload: AutomationPipelineUpdateRequest,
    user: RequireAutomationManage,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    try:
        item = await automation_pipeline_service.update_pipeline(db, user, pipeline_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    await publish_pipeline_rules_updated(
        redis,
        tenant_id=str(user.tenant_id),
        pipeline_id=str(item["id"]),
        action="updated",
        pipeline=item,
    )
    return AutomationPipelineResponse.model_validate(item)


@router.delete("/pipelines/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(
    pipeline_id: uuid.UUID,
    user: RequireAutomationManage,
    db: AsyncSession = Depends(get_db),
):
    await automation_pipeline_service.delete_pipeline(db, user, pipeline_id)


@router.post("/pipelines/dry-run", response_model=PipelineTestRunResponse)
async def dry_run_pipeline_graph(
    payload: PipelineDryRunRequest,
    user: RequireAutomationRun,
    redis: aioredis.Redis = Depends(get_redis),
):
    errors, _warnings = validate_pipeline_document(payload.nodes, payload.edges)
    if errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"errors": errors})
    pipeline = AutomationPipeline(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        name=payload.pipeline_name,
        is_active=True,
        nodes_json=payload.nodes,
        edges_json=payload.edges,
    )
    executed, steps = await pipeline_interpreter_service.run_pipeline(
        pipeline,
        event_type=payload.event_type,
        context=payload.context,
        redis=redis,
        tenant_id=user.tenant_id,
        dry_run=True,
    )
    return PipelineTestRunResponse(
        pipeline_id=pipeline.id,
        pipeline_name=pipeline.name,
        event_type=payload.event_type,
        executed=executed,
        steps=steps,
    )


@router.post("/pipelines/{pipeline_id}/test-run", response_model=PipelineTestRunResponse)
async def test_run_pipeline(
    pipeline_id: uuid.UUID,
    payload: PipelineTestRunRequest,
    user: RequireAutomationRun,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    data = await automation_pipeline_service.get_pipeline(db, user, pipeline_id)
    nodes_json = payload.nodes if payload.nodes is not None else data["nodes_json"]
    edges_json = payload.edges if payload.edges is not None else data["edges_json"]
    if payload.edges is not None:
        normalized_edges: list[dict] = []
        for edge in edges_json:
            normalized = dict(edge)
            normalized.setdefault("from", edge.get("source") or edge.get("from_node"))
            normalized.setdefault("to", edge.get("target") or edge.get("to_node"))
            normalized_edges.append(normalized)
        edges_json = normalized_edges
    pipeline = AutomationPipeline(
        id=data["id"],
        tenant_id=data["tenant_id"],
        name=data["name"],
        description=data["description"],
        is_active=data["is_active"],
        nodes_json=nodes_json,
        edges_json=edges_json,
    )
    executed, steps = await pipeline_interpreter_service.run_pipeline(
        pipeline,
        event_type=payload.event_type,
        context=payload.context,
        redis=redis,
        tenant_id=user.tenant_id,
        dry_run=True,
    )
    return PipelineTestRunResponse(
        pipeline_id=pipeline_id,
        pipeline_name=data["name"],
        event_type=payload.event_type,
        executed=executed,
        steps=steps,
    )
