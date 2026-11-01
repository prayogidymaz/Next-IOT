"""Pydantic schemas for sites API."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SiteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    parent_site_id: uuid.UUID | None = None
    location_json: dict[str, object] = Field(default_factory=dict)
    timezone: str = "UTC"


class SiteUpdate(BaseModel):
    name: str | None = None
    location_json: dict[str, object] | None = None
    timezone: str | None = None
    is_active: bool | None = None


class SiteView(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    slug: str
    parent_site_id: uuid.UUID | None
    location_json: dict[str, object]
    timezone: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PlotCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    crop_type: str = ""
    area_hectares: Decimal = Decimal("0")
    soil_type: str = ""
    planting_date: date | None = None
    expected_harvest_date: date | None = None
    metadata_json: dict[str, object] = Field(default_factory=dict)


class PlotView(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID
    name: str
    crop_type: str
    area_hectares: Decimal
    soil_type: str
    planting_date: date | None
    expected_harvest_date: date | None
    metadata_json: dict[str, object]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SiteMemberInvite(BaseModel):
    user_id: uuid.UUID
    role: str = Field(pattern=r"^(owner|manager|viewer)$")


class SiteReportView(BaseModel):
    site_id: uuid.UUID
    period_days: int
    plot_count: int
    total_area_hectares: float
    active_plots: int
    telemetry_metrics: dict[str, float] = Field(default_factory=dict)
