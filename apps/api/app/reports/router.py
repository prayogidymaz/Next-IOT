"""Reporting studio API."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.reports import template_service
from app.reports.generator import generate_report
from app.reports.schemas import (
    ReportGenerationView,
    ReportScheduleCreate,
    ReportScheduleView,
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportTemplateView,
)

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/templates", response_model=list[ReportTemplateView])
async def list_report_templates(user: RequireAuth, db: DbSession) -> list[ReportTemplateView]:
    rows = await template_service.list_templates(db, user)
    return [ReportTemplateView.model_validate(r) for r in rows]


@router.post("/templates", response_model=ReportTemplateView, status_code=201)
async def create_report_template(user: RequireAuth, db: DbSession, payload: ReportTemplateCreate) -> ReportTemplateView:
    row = await template_service.create_template(db, user, payload)
    return ReportTemplateView.model_validate(row)


@router.get("/templates/{template_id}", response_model=ReportTemplateView)
async def get_report_template(user: RequireAuth, db: DbSession, template_id: uuid.UUID) -> ReportTemplateView:
    row = await template_service.get_template(db, user, template_id)
    return ReportTemplateView.model_validate(row)


@router.patch("/templates/{template_id}", response_model=ReportTemplateView)
async def patch_report_template(
    user: RequireAuth, db: DbSession, template_id: uuid.UUID, payload: ReportTemplateUpdate
) -> ReportTemplateView:
    row = await template_service.update_template(db, user, template_id, payload)
    return ReportTemplateView.model_validate(row)


@router.post("/templates/{template_id}/generate", response_model=ReportGenerationView, status_code=201)
async def generate_report_now(
    user: RequireAuth,
    db: DbSession,
    template_id: uuid.UUID,
    format: str = Query(default="pdf", pattern=r"^(pdf|csv|excel)$"),
) -> ReportGenerationView:
    template = await template_service.get_template(db, user, template_id)
    gen = await generate_report(db, template, format)
    return ReportGenerationView.model_validate(gen)


@router.post("/templates/{template_id}/schedules", response_model=ReportScheduleView, status_code=201)
async def create_schedule(
    user: RequireAuth, db: DbSession, template_id: uuid.UUID, payload: ReportScheduleCreate
) -> ReportScheduleView:
    row = await template_service.add_schedule(db, user, template_id, payload)
    return ReportScheduleView.model_validate(row)


@router.get("/templates/{template_id}/history", response_model=list[ReportGenerationView])
async def report_history(user: RequireAuth, db: DbSession, template_id: uuid.UUID) -> list[ReportGenerationView]:
    rows = await template_service.list_generations(db, user, template_id)
    return [ReportGenerationView.model_validate(r) for r in rows]
