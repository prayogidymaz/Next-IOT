"""Scheduled analytics report CRUD + scheduler tick."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.models import ScheduledReport
from app.auth.dependencies import CurrentUser
from app.rules.trigger_match import cron_due
from app.types.json_types import JsonObject

logger = logging.getLogger(__name__)


class ScheduledReportCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    report_type: str = Field(pattern="^(telemetry|alerts|yield|energy)$")
    schedule_cron: str = Field(min_length=5, max_length=128)
    recipients: list[str] = Field(default_factory=list)
    filter_json: JsonObject = Field(default_factory=dict)
    enabled: bool = True


class ScheduledReportUpdate(BaseModel):
    name: str | None = None
    report_type: str | None = Field(default=None, pattern="^(telemetry|alerts|yield|energy)$")
    schedule_cron: str | None = None
    recipients: list[str] | None = None
    filter_json: JsonObject | None = None
    enabled: bool | None = None


class ScheduledReportView(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    report_type: str
    schedule_cron: str
    recipients: list[str]
    filter_json: JsonObject
    enabled: bool
    last_run_at: datetime | None
    created_at: datetime
    updated_at: datetime


def _view(row: ScheduledReport) -> ScheduledReportView:
    recipients = row.recipients if isinstance(row.recipients, list) else []
    clean_recipients = [str(x) for x in recipients]
    return ScheduledReportView(
        id=row.id,
        tenant_id=row.tenant_id,
        name=row.name,
        report_type=row.report_type,
        schedule_cron=row.schedule_cron,
        recipients=clean_recipients,
        filter_json=row.filter_json if isinstance(row.filter_json, dict) else {},
        enabled=row.enabled,
        last_run_at=row.last_run_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


async def create_scheduled_report(
    db: AsyncSession,
    user: CurrentUser,
    payload: ScheduledReportCreate,
) -> ScheduledReportView:
    row = ScheduledReport(
        tenant_id=user.tenant_id,
        name=payload.name,
        report_type=payload.report_type,
        schedule_cron=payload.schedule_cron,
        recipients=payload.recipients,
        filter_json=payload.filter_json,
        enabled=payload.enabled,
    )
    db.add(row)
    await db.flush()
    return _view(row)


async def list_scheduled_reports(db: AsyncSession, user: CurrentUser) -> list[ScheduledReportView]:
    rows = await db.scalars(
        select(ScheduledReport)
        .where(ScheduledReport.tenant_id == user.tenant_id)
        .order_by(ScheduledReport.name)
    )
    return [_view(row) for row in rows.all()]


async def _get_report(db: AsyncSession, user: CurrentUser, report_id: uuid.UUID) -> ScheduledReport:
    row = await db.scalar(select(ScheduledReport).where(ScheduledReport.id == report_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    if not user.is_super_admin and row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return row


async def update_scheduled_report(
    db: AsyncSession,
    user: CurrentUser,
    report_id: uuid.UUID,
    payload: ScheduledReportUpdate,
) -> ScheduledReportView:
    row = await _get_report(db, user, report_id)
    if payload.name is not None:
        row.name = payload.name
    if payload.report_type is not None:
        row.report_type = payload.report_type
    if payload.schedule_cron is not None:
        row.schedule_cron = payload.schedule_cron
    if payload.recipients is not None:
        row.recipients = payload.recipients
    if payload.filter_json is not None:
        row.filter_json = payload.filter_json
    if payload.enabled is not None:
        row.enabled = payload.enabled
    await db.flush()
    return _view(row)


async def delete_scheduled_report(db: AsyncSession, user: CurrentUser, report_id: uuid.UUID) -> None:
    row = await _get_report(db, user, report_id)
    await db.delete(row)


async def run_scheduled_reports_tick(db: AsyncSession, now: datetime | None = None) -> int:
    """Fire due reports (email stub — logs only)."""
    tick = now or datetime.now(tz=UTC)
    rows = await db.scalars(select(ScheduledReport).where(ScheduledReport.enabled.is_(True)))
    fired = 0
    for row in rows.all():
        if not cron_due(row.schedule_cron, tick, last_executed_at=row.last_run_at):
            continue
        logger.info(
            "Scheduled report %s (%s) due for tenant %s recipients=%s",
            row.id,
            row.report_type,
            row.tenant_id,
            row.recipients,
        )
        row.last_run_at = tick
        fired += 1
    return fired
