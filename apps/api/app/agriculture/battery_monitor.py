"""Low-battery checks for LoRa sensors."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from app.agriculture.models import AgriSensorDevice
from app.agriculture.notification_dispatcher import AgriNotificationDispatcher
from app.database import async_session
from app.types.redis_client import RedisClient

LOW_VOLTAGE = Decimal("3.20")


async def check_batteries(redis: RedisClient) -> int:
    sent = 0
    async with async_session() as db:
        rows = await db.scalars(
            select(AgriSensorDevice).where(
                AgriSensorDevice.last_battery_voltage.is_not(None),
                AgriSensorDevice.last_battery_voltage < LOW_VOLTAGE,
            )
        )
        dispatcher = AgriNotificationDispatcher(db, redis)
        for sensor in rows.all():
            if await dispatcher.send_low_battery_warning(sensor.id):
                sent += 1
    return sent
