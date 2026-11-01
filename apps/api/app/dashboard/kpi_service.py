"""Tenant dashboard KPI aggregation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.models.alarm import Alarm, AlarmStatus
from app.models.device import Device, DeviceStatus
from app.models.telemetry_reading import TelemetryReading


async def get_tenant_kpi(db: AsyncSession, user: CurrentUser, tenant_id: uuid.UUID | None) -> dict[str, float | int | list[dict[str, int | str]]]:
    tid = tenant_id or user.tenant_id
    if tid != user.tenant_id and not user.is_super_admin:
        tid = user.tenant_id

    devices_online = await db.scalar(
        select(func.count()).select_from(Device).where(Device.tenant_id == tid, Device.status == DeviceStatus.ONLINE)
    )
    device_total = await db.scalar(select(func.count()).select_from(Device).where(Device.tenant_id == tid))
    active_alarms = await db.scalar(
        select(func.count()).select_from(Alarm).where(Alarm.tenant_id == tid, Alarm.status == AlarmStatus.ACTIVE)
    )

    since = datetime.now(tz=UTC) - timedelta(hours=24)
    msg_count = await db.scalar(
        select(func.count())
        .select_from(TelemetryReading)
        .where(TelemetryReading.tenant_id == tid, TelemetryReading.recorded_at >= since)
    )
    messages_per_min = float(msg_count or 0) / 1440.0

    reading_rows = int(msg_count or 0)
    data_volume_today_gb = float(Decimal(reading_rows) * Decimal("0.000002"))

    heatmap: list[dict[str, int | str]] = []
    for hour in range(24):
        bucket_start = datetime.now(tz=UTC).replace(minute=0, second=0, microsecond=0) - timedelta(hours=23 - hour)
        bucket_end = bucket_start + timedelta(hours=1)
        online_at = await db.scalar(
            select(func.count())
            .select_from(Device)
            .where(
                Device.tenant_id == tid,
                Device.status == DeviceStatus.ONLINE,
                Device.last_seen_at >= bucket_start,
                Device.last_seen_at < bucket_end,
            )
        )
        heatmap.append({"hour": bucket_start.strftime("%H:00"), "online": int(online_at or 0)})

    return {
        "devices_online": int(devices_online or 0),
        "device_total": int(device_total or 0),
        "messages_per_min": round(messages_per_min, 2),
        "active_alarms": int(active_alarms or 0),
        "data_volume_today_gb": round(data_volume_today_gb, 3),
        "devices_online_history": heatmap,
    }
