"""Seed demo telemetry readings for dev dashboards and charts."""

import asyncio
import logging
import math
from datetime import UTC, datetime, timedelta

import redis.asyncio as aioredis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.models.device import Device, DeviceStatus
from app.models.telemetry_reading import TelemetryReading
from app.models.tenant import Tenant
from app.telemetry.cache import cache_latest_telemetry

logger = logging.getLogger(__name__)

DEMO_DEVICE_NAME = "Demo Sensor Node"


async def ensure_demo_telemetry(db: AsyncSession, redis: aioredis.Redis) -> bool:
    """Insert time-series demo telemetry for the seeded tenant. Idempotent."""
    tenant = await db.scalar(select(Tenant).where(Tenant.slug == settings.seed_tenant_slug))
    if tenant is None:
        return False

    device = await db.scalar(
        select(Device).where(Device.tenant_id == tenant.id, Device.name == DEMO_DEVICE_NAME)
    )
    if device is None:
        device = Device(
            tenant_id=tenant.id,
            name=DEMO_DEVICE_NAME,
            device_type="sensor",
            status=DeviceStatus.ONLINE,
            last_seen_at=datetime.now(UTC),
        )
        db.add(device)
        await db.flush()

    count = await db.scalar(
        select(func.count()).select_from(TelemetryReading).where(TelemetryReading.device_id == device.id)
    )
    if count and count > 0:
        logger.debug("Telemetry seed skipped: device %s already has readings", device.id)
        return False

    now = datetime.now(UTC)
    readings: list[TelemetryReading] = []
    points = 336  # 7 days @ 30-minute intervals

    for i in range(points):
        recorded_at = now - timedelta(minutes=30 * (points - 1 - i))
        phase = i / 10
        metrics = {
            "temperature": round(22 + 6 * math.sin(phase), 1),
            "humidity": round(55 + 15 * math.cos(phase / 1.2), 1),
            "battery": round(max(15.0, 100 - i * 0.25), 1),
            "roll": round(math.sin(phase / 2) * 18, 1),
            "pitch": round(math.cos(phase / 2) * 12, 1),
            "yaw": round((i * 2.7) % 360, 1),
            "latitude": round(-6.2088 + 0.002 * math.sin(phase / 5), 6),
            "longitude": round(106.8456 + 0.002 * math.cos(phase / 5), 6),
            "altitude_m": round(28 + 3 * math.sin(phase / 3), 1),
        }
        readings.append(
            TelemetryReading(
                device_id=device.id,
                tenant_id=tenant.id,
                recorded_at=recorded_at,
                metrics=metrics,
            )
        )

    db.add_all(readings)
    await db.flush()

    latest = readings[-1]
    await cache_latest_telemetry(
        redis,
        device_id=str(device.id),
        tenant_id=str(tenant.id),
        recorded_at=latest.recorded_at,
        metrics=latest.metrics,
        reading_id=str(latest.id),
    )
    await db.commit()
    logger.info("Seeded %d telemetry readings for demo device %s", len(readings), device.id)
    return True


async def run_telemetry_seed(redis: aioredis.Redis) -> bool:
    async with async_session() as db:
        return await ensure_demo_telemetry(db, redis)


def main() -> None:
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)

    async def _run() -> bool:
        try:
            return await run_telemetry_seed(redis)
        finally:
            await redis.aclose()

    created = asyncio.run(_run())
    if created:
        print("Demo telemetry seeded for Demo Sensor Node")
    else:
        print("Demo telemetry already present or tenant missing")


if __name__ == "__main__":
    main()
