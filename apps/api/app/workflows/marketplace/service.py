"""Workflow template marketplace."""

from __future__ import annotations

import uuid
from typing import cast

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.mesh.workflow_registry import reload_workflows
from app.models.mesh_workflow import MeshWorkflow
from app.types.json_types import JsonObject
from app.workflows.marketplace.models import WorkflowTemplate, WorkflowTemplateDownload, WorkflowTemplateRating
from app.workflows.marketplace.schemas import WorkflowTemplateView


def _template_view(row: WorkflowTemplate) -> WorkflowTemplateView:
    tags = row.tags_json if isinstance(row.tags_json, list) else []
    tag_strings = [str(item) for item in tags]
    snap = row.snapshot_json if isinstance(row.snapshot_json, dict) else {}
    return WorkflowTemplateView(
        id=row.id,
        name=row.name,
        description=row.description,
        category=row.category,
        tags_json=tag_strings,
        author_tenant_id=row.author_tenant_id,
        snapshot_json=cast(JsonObject, snap),
        downloads_count=row.downloads_count,
        rating_avg=row.rating_avg,
        rating_count=row.rating_count,
        published=row.published,
        created_at=row.created_at,
        locale=row.locale,
    )


class MarketplaceService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def publish(
        self,
        workflow_id: uuid.UUID,
        metadata_dict: JsonObject,
        user: CurrentUser,
    ) -> WorkflowTemplate:
        mesh = await self._db.scalar(select(MeshWorkflow).where(MeshWorkflow.id == workflow_id))
        if mesh is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
        if mesh.tenant_id != user.tenant_id and not user.is_super_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        name_raw = metadata_dict.get("name")
        category_raw = metadata_dict.get("category")
        if not isinstance(name_raw, str) or not isinstance(category_raw, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name and category required")
        desc_raw = metadata_dict.get("description")
        tags_raw = metadata_dict.get("tags")
        locale_raw = metadata_dict.get("locale")
        tags: list[str] = [str(t) for t in tags_raw] if isinstance(tags_raw, list) else []
        snapshot: JsonObject = {
            "name": mesh.name,
            "description": mesh.description,
            "definition": cast(JsonObject, mesh.definition) if isinstance(mesh.definition, dict) else {},
        }
        row = WorkflowTemplate(
            name=name_raw,
            description=str(desc_raw) if isinstance(desc_raw, str) else "",
            category=category_raw,
            tags_json=tags,
            author_tenant_id=user.tenant_id,
            snapshot_json=snapshot,
            published=True,
            locale=str(locale_raw) if isinstance(locale_raw, str) else "id",
        )
        self._db.add(row)
        await self._db.flush()
        return row

    async def unpublish(self, template_id: uuid.UUID, user: CurrentUser) -> WorkflowTemplate:
        row = await self._db.get(WorkflowTemplate, template_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        if row.author_tenant_id != user.tenant_id and not user.is_super_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        row.published = False
        await self._db.flush()
        return row

    async def list_templates(
        self,
        category: str | None,
        locale: str,
        sort_by: str,
        limit: int,
    ) -> list[WorkflowTemplate]:
        query = select(WorkflowTemplate).where(WorkflowTemplate.published.is_(True))
        if category:
            query = query.where(WorkflowTemplate.category == category)
        if locale:
            query = query.where(WorkflowTemplate.locale == locale)
        if sort_by == "rating":
            query = query.order_by(WorkflowTemplate.rating_avg.desc())
        else:
            query = query.order_by(WorkflowTemplate.downloads_count.desc())
        query = query.limit(limit)
        rows = await self._db.scalars(query)
        return list(rows.all())

    async def get(self, template_id: uuid.UUID) -> WorkflowTemplate:
        row = await self._db.get(WorkflowTemplate, template_id)
        if row is None or not row.published:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        return row

    async def download(
        self,
        template_id: uuid.UUID,
        user: CurrentUser,
        target_tenant_id: uuid.UUID | None,
    ) -> MeshWorkflow:
        template = await self.get(template_id)
        tenant_id = target_tenant_id or user.tenant_id
        if tenant_id != user.tenant_id and not user.is_super_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        snap = template.snapshot_json if isinstance(template.snapshot_json, dict) else {}
        def_raw = snap.get("definition")
        definition = def_raw if isinstance(def_raw, dict) else {}
        name_raw = snap.get("name")
        desc_raw = snap.get("description")
        mesh = MeshWorkflow(
            tenant_id=tenant_id,
            name=str(name_raw) if isinstance(name_raw, str) else template.name,
            description=str(desc_raw) if isinstance(desc_raw, str) else template.description,
            enabled=False,
            definition=definition,
        )
        self._db.add(mesh)
        template.downloads_count += 1
        self._db.add(
            WorkflowTemplateDownload(
                template_id=template.id,
                downloader_tenant_id=tenant_id,
            )
        )
        await self._db.flush()
        await reload_workflows(self._db, tenant_id)
        return mesh

    async def rate(
        self,
        template_id: uuid.UUID,
        user: CurrentUser,
        rating: int,
        review: str,
    ) -> WorkflowTemplateRating:
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be 1-5")
        template = await self.get(template_id)
        existing = await self._db.scalar(
            select(WorkflowTemplateRating).where(
                WorkflowTemplateRating.template_id == template_id,
                WorkflowTemplateRating.rater_tenant_id == user.tenant_id,
            )
        )
        if existing is not None:
            old_rating = existing.rating
            existing.rating = rating
            existing.review_text = review
            total = template.rating_avg * template.rating_count - old_rating + rating
            template.rating_avg = total / max(template.rating_count, 1)
            await self._db.flush()
            return existing
        row = WorkflowTemplateRating(
            template_id=template_id,
            rater_tenant_id=user.tenant_id,
            rating=rating,
            review_text=review,
        )
        self._db.add(row)
        total = template.rating_avg * template.rating_count + rating
        template.rating_count += 1
        template.rating_avg = total / template.rating_count
        await self._db.flush()
        return row

    async def search(self, query: str, filters_dict: JsonObject) -> list[WorkflowTemplate]:
        pattern = f"%{query.strip()}%"
        stmt = select(WorkflowTemplate).where(
            WorkflowTemplate.published.is_(True),
            or_(WorkflowTemplate.name.ilike(pattern), WorkflowTemplate.description.ilike(pattern)),
        )
        category = filters_dict.get("category")
        if isinstance(category, str) and category:
            stmt = stmt.where(WorkflowTemplate.category == category)
        locale = filters_dict.get("locale")
        if isinstance(locale, str) and locale:
            stmt = stmt.where(WorkflowTemplate.locale == locale)
        stmt = stmt.order_by(WorkflowTemplate.downloads_count.desc()).limit(50)
        rows = await self._db.scalars(stmt)
        return list(rows.all())
