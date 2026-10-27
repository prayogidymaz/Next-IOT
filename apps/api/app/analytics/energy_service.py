"""Energy analytics from telemetry power metrics."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.export_service import metric_power_watts
from app.models.device import Device
from app.models.telemetry_reading import TelemetryReading


class EnergyResult(BaseModel):
    device_id: uuid.UUID
    start: datetime
    end: datetime
    kwh_total: float
    cost_idr: float
    sample_count: int


class EnergySummaryItem(BaseModel):
    device_id: uuid.UUID
    device_name: str
    kwh_total: float
    cost_idr: float


class EnergySummaryResult(BaseModel):
    farm_id: uuid.UUID | None
    period_days: int
    devices: list[EnergySummaryItem]
    kwh_total: float
    cost_idr: float


def cost_estimate(kwh: float, tariff_per_kwh: float = 1500.0) -> float:
    return round(kwh * tariff_per_kwh, 2)


def _integrate_kwh(readings: list[TelemetryReading]) -> tuple[float, int]:
    if len(readings) < 2:
        return 0.0, len(readings)
    total_wh = 0.0
    count = 0
    prev = readings[0]
    prev_w = metric_power_watts(prev.metrics if isinstance(prev.metrics, dict) else {})
    for current in readings[1:]:
        metrics = current.metrics if isinstance(current.metrics, dict) else {}
        watts = metric_power_watts(metrics)
        if prev_w is not None and watts is not None:
            delta_h = (current.recorded_at - prev.recorded_at).total_seconds() / 3600.0
            if delta_h > 0:
                avg_w = (prev_w + watts) / 2.0
                total_wh += avg_w * delta_h
                count += 1
        prev = current
        prev_w = watts
    return total_wh / 1000.0, count


async def calculate_energy(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID,
    start: datetime,
    end: datetime,
    tariff_per_kwh: float = 1500.0,
) -> EnergyResult:
    rows = await db.scalars(
        select(TelemetryReading)
        .where(
            TelemetryReading.tenant_id == tenant_id,
            TelemetryReading.device_id == device_id,
            TelemetryReading.recorded_at >= start,
            TelemetryReading.recorded_at <= end,
        )
        .order_by(TelemetryReading.recorded_at.asc())
    )
    readings = list(rows.all())
    kwh, sample_count = _integrate_kwh(readings)
    return EnergyResult(
        device_id=device_id,
        start=start,
        end=end,
        kwh_total=round(kwh, 4),
        cost_idr=cost_estimate(kwh, tariff_per_kwh),
        sample_count=sample_count,
    )


async def energy_summary_for_farm(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    farm_id: uuid.UUID | None,
    period_days: int,
    tariff_per_kwh: float = 1500.0,
) -> EnergySummaryResult:
    end = datetime.now(tz=UTC)
    start = end - timedelta(days=period_days)
    stmt = select(Device).where(Device.tenant_id == tenant_id)
    devices = list((await db.scalars(stmt)).all())
    items: list[EnergySummaryItem] = []
    total_kwh = 0.0
    for device in devices:
        result = await calculate_energy(db, tenant_id, device.id, start, end, tariff_per_kwh)
        if result.kwh_total <= 0:
            continue
        items.append(
            EnergySummaryItem(
                device_id=device.id,
                device_name=device.name,
                kwh_total=result.kwh_total,
                cost_idr=result.cost_idr,
            )
        )
        total_kwh += result.kwh_total
    return EnergySummaryResult(
        farm_id=farm_id,
        period_days=period_days,
        devices=items,
        kwh_total=round(total_kwh, 4),
        cost_idr=cost_estimate(total_kwh, tariff_per_kwh),
    )
