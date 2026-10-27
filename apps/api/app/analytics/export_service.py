"""CSV export for telemetry, alerts, and yield."""

from __future__ import annotations

import csv
import io
import uuid
from collections.abc import AsyncIterator
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agriculture.models import AgriPlot, AgriYieldRecord
from app.models.alarm import Alarm
from app.models.telemetry_reading import TelemetryReading
from app.types.json_types import JsonValue, json_value_to_float


async def export_telemetry_csv(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID,
    metric_key: str,
    start: datetime,
    end: datetime,
) -> bytes:
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
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["recorded_at", "device_id", "metric", "value"])
    for row in rows.all():
        metrics = row.metrics
        value = metrics.get(metric_key) if isinstance(metrics, dict) else None
        if value is None:
            continue
        writer.writerow([row.recorded_at.isoformat(), str(device_id), metric_key, value])
    return buffer.getvalue().encode("utf-8")


async def iter_telemetry_csv_chunks(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID,
    metric_key: str,
    start: datetime,
    end: datetime,
    chunk_size: int = 500,
) -> AsyncIterator[bytes]:
    yield b"recorded_at,device_id,metric,value\n"
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
    batch: list[str] = []
    for row in rows.all():
        metrics = row.metrics
        if not isinstance(metrics, dict):
            continue
        raw = metrics.get(metric_key)
        if raw is None:
            continue
        batch.append(f"{row.recorded_at.isoformat()},{device_id},{metric_key},{raw}\n")
        if len(batch) >= chunk_size:
            yield "".join(batch).encode("utf-8")
            batch = []
    if batch:
        yield "".join(batch).encode("utf-8")


async def export_alerts_csv(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    start: datetime,
    end: datetime,
) -> bytes:
    rows = await db.scalars(
        select(Alarm)
        .where(
            Alarm.tenant_id == tenant_id,
            Alarm.occurred_at >= start,
            Alarm.occurred_at <= end,
        )
        .order_by(Alarm.occurred_at.asc())
    )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["occurred_at", "title", "severity", "status", "device_id"])
    for row in rows.all():
        writer.writerow(
            [
                row.occurred_at.isoformat(),
                row.title,
                row.severity,
                row.status,
                str(row.device_id) if row.device_id else "",
            ]
        )
    return buffer.getvalue().encode("utf-8")


async def export_yield_csv(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    farm_id: uuid.UUID,
    year: int,
) -> bytes:
    plot_ids = await db.scalars(select(AgriPlot.id).where(AgriPlot.farm_id == farm_id))
    ids = list(plot_ids.all())
    if not ids:
        return b"plot_id,harvest_date,quantity_kg,quality_grade\n"
    rows = await db.scalars(
        select(AgriYieldRecord)
        .where(
            AgriYieldRecord.plot_id.in_(ids),
            AgriYieldRecord.harvest_date >= date(year, 1, 1),
            AgriYieldRecord.harvest_date < date(year + 1, 1, 1),
        )
        .order_by(AgriYieldRecord.harvest_date.asc())
    )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["plot_id", "harvest_date", "quantity_kg", "quality_grade"])
    for row in rows.all():
        writer.writerow(
            [
                str(row.plot_id),
                row.harvest_date.isoformat(),
                row.quantity_kg,
                row.quality_grade,
            ]
        )
    return buffer.getvalue().encode("utf-8")


def metric_power_watts(metrics: dict[str, JsonValue]) -> float | None:
    for key in ("power_w", "power", "watts"):
        val = json_value_to_float(metrics.get(key))
        if val is not None:
            return val
    return None
