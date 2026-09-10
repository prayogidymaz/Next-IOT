import asyncio
import logging

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import async_session
from app.devices.events import emit_device_event
from app.devices.liveness import is_lively
from app.models.device import Device, DeviceStatus

logger = logging.getLogger(__name__)


async def mark_stale_devices_offline(redis: aioredis.Redis) -> int:
    """Mark online devices as offline when Redis liveness TTL has expired."""
    marked = 0
    async with async_session() as session:
        result = await session.scalars(
            select(Device).where(Device.status == DeviceStatus.ONLINE)
        )
        devices = result.all()

        for device in devices:
            if await is_lively(redis, str(device.id)):
                continue

            previous = device.status
            device.status = DeviceStatus.OFFLINE
            marked += 1
            await emit_device_event(
                redis,
                "device.offline",
                device_id=str(device.id),
                tenant_id=str(device.tenant_id),
                extra={"previous_status": previous},
            )
            logger.info("Device %s marked offline (liveness expired)", device.id)

        if marked:
            await session.commit()

    return marked


async def offline_checker_loop(redis: aioredis.Redis, stop_event: asyncio.Event) -> None:
    interval = settings.device_offline_check_interval_seconds
    while not stop_event.is_set():
        try:
            count = await mark_stale_devices_offline(redis)
            if count:
                logger.info("Offline checker: marked %d device(s) offline", count)
        except Exception:
            logger.exception("Offline checker iteration failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue
