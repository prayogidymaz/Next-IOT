"""Sustainability API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CarbonSeriesPoint(BaseModel):
    recorded_at: datetime
    co2_equivalent_kg: Decimal
    source_type: str


class WaterSeriesPoint(BaseModel):
    plot_id: uuid.UUID | None
    liters_used: Decimal
    source: str
    recorded_at: datetime


class EsgScorecardView(BaseModel):
    id: uuid.UUID
    period_month: str
    environmental_score: Decimal
    social_score: Decimal
    governance_score: Decimal
    overall_grade: str
    generated_at: datetime
    report_pdf_url: str | None

    model_config = {"from_attributes": True}
