"""Workflow analytics HTTP routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.workflows.analytics.schemas import (
    FailureReportView,
    SavingsReportView,
    TimelineDataView,
    WorkflowStatsView,
)
from app.workflows.analytics.service import WorkflowAnalyticsService

router = APIRouter(prefix="/api/v1/analytics/workflows", tags=["workflow-analytics"])


@router.get("/top-fired", response_model=list[WorkflowStatsView])
async def top_fired_workflows(
    user: RequireAuth,
    db: DbSession,
    period_days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[WorkflowStatsView]:
    service = WorkflowAnalyticsService(db)
    return await service.top_fired_workflows(user.tenant_id, period_days, limit)


@router.get("/{workflow_id}/timeline", response_model=TimelineDataView)
async def workflow_timeline(
    user: RequireAuth,
    db: DbSession,
    workflow_id: uuid.UUID,
    period_days: int = Query(default=7, ge=1, le=90),
) -> TimelineDataView:
    service = WorkflowAnalyticsService(db)
    return await service.workflow_timeline(workflow_id, user, period_days)


@router.get("/{workflow_id}/savings", response_model=SavingsReportView)
async def workflow_savings(
    user: RequireAuth,
    db: DbSession,
    workflow_id: uuid.UUID,
) -> SavingsReportView:
    service = WorkflowAnalyticsService(db)
    return await service.savings_per_workflow(workflow_id, user)


@router.get("/{workflow_id}/failures", response_model=FailureReportView)
async def workflow_failures(
    user: RequireAuth,
    db: DbSession,
    workflow_id: uuid.UUID,
) -> FailureReportView:
    service = WorkflowAnalyticsService(db)
    return await service.failure_analysis(workflow_id, user)
