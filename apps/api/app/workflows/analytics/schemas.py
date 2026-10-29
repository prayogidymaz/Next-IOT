"""Workflow analytics API schemas."""

from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel, Field

from app.types.json_types import JsonObject


class WorkflowStatsView(BaseModel):
    workflow_id: uuid.UUID
    name: str
    fire_count: int
    success_count: int
    fail_count: int
    avg_duration_ms: float
    savings_idr_estimate: float


class TimelinePointView(BaseModel):
    date: date
    fire_count: int
    success_count: int


class TimelineDataView(BaseModel):
    points: list[TimelinePointView] = Field(default_factory=list)


class SavingsReportView(BaseModel):
    water_liters_saved: float
    kwh_saved: float
    idr_total: float
    calculation_breakdown: JsonObject


class FailureReportView(BaseModel):
    common_errors: list[str]
    failed_at_step: str | None
    suggested_fix: str
    failure_rate: float
