"""Dashboard KPI API."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.auth.dependencies import RequireAuth
from app.dashboard.kpi_service import get_tenant_kpi
from app.deps import DbSession

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


class HeatmapPoint(BaseModel):
    hour: str
    online: int


class DashboardKpiView(BaseModel):
    devices_online: int
    device_total: int
    messages_per_min: float
    active_alarms: int
    data_volume_today_gb: float
    devices_online_history: list[HeatmapPoint] = Field(default_factory=list)


TenantQuery = Annotated[uuid.UUID | None, Query()]


@router.get("/kpi", response_model=DashboardKpiView)
async def dashboard_kpi(user: RequireAuth, db: DbSession, tenant_id: TenantQuery = None) -> DashboardKpiView:
    raw = await get_tenant_kpi(db, user, tenant_id)
    return DashboardKpiView(
        devices_online=int(raw["devices_online"]),
        device_total=int(raw["device_total"]),
        messages_per_min=float(raw["messages_per_min"]),
        active_alarms=int(raw["active_alarms"]),
        data_volume_today_gb=float(raw["data_volume_today_gb"]),
        devices_online_history=[HeatmapPoint(hour=str(p["hour"]), online=int(p["online"])) for p in raw["devices_online_history"]],
    )
