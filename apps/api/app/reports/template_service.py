"""Report template CRUD."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.reports.models import ReportGeneration, ReportSchedule, ReportTemplate
from app.reports.schemas import ReportScheduleCreate, ReportTemplateCreate, ReportTemplateUpdate


async def list_templates(db: AsyncSession, user: CurrentUser) -> list[ReportTemplate]:
    rows = await db.scalars(
        select(ReportTemplate).where(ReportTemplate.tenant_id == user.tenant_id).order_by(ReportTemplate.created_at.desc())
    )
    return list(rows.all())


async def create_template(db: AsyncSession, user: CurrentUser, payload: ReportTemplateCreate) -> ReportTemplate:
    row = ReportTemplate(
        tenant_id=user.tenant_id,
        name=payload.name,
        description=payload.description,
        config_json=payload.config_json,
        created_by=user.user_id,
        is_public=payload.is_public,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def get_template(db: AsyncSession, user: CurrentUser, template_id: uuid.UUID) -> ReportTemplate:
    row = await db.get(ReportTemplate, template_id)
    if row is None or row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return row


async def update_template(db: AsyncSession, user: CurrentUser, template_id: uuid.UUID, payload: ReportTemplateUpdate) -> ReportTemplate:
    row = await get_template(db, user, template_id)
    if payload.name is not None:
        row.name = payload.name
    if payload.description is not None:
        row.description = payload.description
    if payload.config_json is not None:
        row.config_json = payload.config_json
    if payload.is_public is not None:
        row.is_public = payload.is_public
    await db.commit()
    await db.refresh(row)
    return row


async def add_schedule(db: AsyncSession, user: CurrentUser, template_id: uuid.UUID, payload: ReportScheduleCreate) -> ReportSchedule:
    await get_template(db, user, template_id)
    row = ReportSchedule(
        template_id=template_id,
        cron_expression=payload.cron_expression,
        recipients_json=payload.recipients,
        format=payload.format,
        enabled=payload.enabled,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def list_generations(db: AsyncSession, user: CurrentUser, template_id: uuid.UUID) -> list[ReportGeneration]:
    await get_template(db, user, template_id)
    rows = await db.scalars(
        select(ReportGeneration).where(ReportGeneration.template_id == template_id).order_by(ReportGeneration.generated_at.desc())
    )
    return list(rows.all())
