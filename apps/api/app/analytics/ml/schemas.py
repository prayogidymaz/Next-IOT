"""Pydantic schemas for ML analytics API."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field

from app.types.json_types import JsonObject


class AnomalySeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class YieldForecast(BaseModel):
    plot_id: uuid.UUID
    horizon_days: int
    estimated_kg: float
    confidence_interval: tuple[float, float]
    risk_factors: list[str] = Field(default_factory=list)
    model_version: str = "lr-v1"
    forecast_date: date


class Anomaly(BaseModel):
    device_id: uuid.UUID
    detected_at: datetime
    metric: str
    value: float
    expected_range: tuple[float, float]
    severity: str
    score: float


class OptimizationReport(BaseModel):
    tenant_id: uuid.UUID
    period_days: int
    energy_kwh_saved_idr: Decimal
    water_liter_saved_idr: Decimal
    fertilizer_rec_kg: float
    total_potential_saving_idr: Decimal
    recommendations: JsonObject = Field(default_factory=dict)
