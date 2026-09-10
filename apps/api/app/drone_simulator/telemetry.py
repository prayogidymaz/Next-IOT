"""Internal telemetry publishing for the drone flight simulator."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.devices.events import emit_device_event
from app.devices.liveness import touch_liveness
from app.devices.state_machine import should_emit_online
from app.models.device import Device, DeviceStatus
from app.models.telemetry_reading import TelemetryReading
from app.telemetry.cache import cache_latest_telemetry


async def ensure_device_online(db: AsyncSession, redis: aioredis.Redis, device: Device) -> None:
    previous = device.status
    now = datetime.now(UTC)
    device.status = DeviceStatus.ONLINE
    device.last_seen_at = now
    await touch_liveness(redis, str(device.id))

    if should_emit_online(previous, device.status):
        await emit_device_event(
            redis,
            "device.online",
            device_id=str(device.id),
            tenant_id=str(device.tenant_id),
            extra={"previous_status": previous, "source": "drone_simulator"},
        )


async def publish_simulated_telemetry(
    db: AsyncSession,
    redis: aioredis.Redis,
    *,
    device: Device,
    metrics: dict[str, Any],
    flight_event: str | None = None,
) -> None:
    recorded_at = datetime.now(UTC)
    reading = TelemetryReading(
        device_id=device.id,
        tenant_id=device.tenant_id,
        recorded_at=recorded_at,
        metrics=metrics,
    )
    db.add(reading)
    await db.flush()

    await cache_latest_telemetry(
        redis,
        device_id=str(device.id),
        tenant_id=str(device.tenant_id),
        recorded_at=recorded_at,
        metrics=metrics,
        reading_id=str(reading.id),
    )
    device.last_seen_at = recorded_at
    await touch_liveness(redis, str(device.id))

    if flight_event:
        await emit_device_event(
            redis,
            flight_event,
            device_id=str(device.id),
            tenant_id=str(device.tenant_id),
            extra={"metrics": metrics},
        )

    await db.commit()
