"""Marketplace HTTP routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, Response, status

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.mesh.workflow_service import _to_view
from app.mesh.workflow_schema import MeshWorkflowRecordView
from app.workflows.marketplace.schemas import (
    DownloadTemplateBody,
    PublishTemplateBody,
    RateTemplateBody,
    WorkflowTemplateView,
)
from app.workflows.marketplace.service import MarketplaceService, _template_view

router = APIRouter(prefix="/api/v1/marketplace", tags=["workflow-marketplace"])


@router.get("/templates", response_model=list[WorkflowTemplateView])
async def list_templates(
    db: DbSession,
    user: RequireAuth,
    category: str | None = None,
    locale: str = "id",
    sort: str = Query(default="downloads", alias="sort"),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[WorkflowTemplateView]:
    _ = user
    service = MarketplaceService(db)
    rows = await service.list_templates(category, locale, sort, limit)
    return [_template_view(row) for row in rows]


@router.get("/templates/{template_id}", response_model=WorkflowTemplateView)
async def get_template(db: DbSession, user: RequireAuth, template_id: uuid.UUID) -> WorkflowTemplateView:
    _ = user
    service = MarketplaceService(db)
    row = await service.get(template_id)
    return _template_view(row)


@router.post("/publish", response_model=WorkflowTemplateView, status_code=201)
async def publish_template(
    user: RequireAuth,
    db: DbSession,
    body: PublishTemplateBody,
) -> WorkflowTemplateView:
    service = MarketplaceService(db)
    metadata: dict[str, object] = {
        "name": body.name,
        "description": body.description,
        "category": body.category,
        "tags": body.tags,
        "locale": body.locale,
    }
    row = await service.publish(body.workflow_id, metadata, user)
    return _template_view(row)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def unpublish_template(
    user: RequireAuth,
    db: DbSession,
    template_id: uuid.UUID,
) -> Response:
    service = MarketplaceService(db)
    await service.unpublish(template_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/templates/{template_id}/download", response_model=MeshWorkflowRecordView)
async def download_template(
    user: RequireAuth,
    db: DbSession,
    template_id: uuid.UUID,
    body: DownloadTemplateBody,
) -> MeshWorkflowRecordView:
    service = MarketplaceService(db)
    mesh = await service.download(template_id, user, body.target_tenant_id)
    return _to_view(mesh)


@router.post("/templates/{template_id}/rate", status_code=204, response_class=Response)
async def rate_template(
    user: RequireAuth,
    db: DbSession,
    template_id: uuid.UUID,
    body: RateTemplateBody,
) -> Response:
    service = MarketplaceService(db)
    await service.rate(template_id, user, body.rating, body.review)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
