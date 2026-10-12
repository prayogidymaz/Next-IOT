"""BMKG-based weather warnings."""

from __future__ import annotations

from sqlalchemy import select

from app.agriculture.bmkg_weather import get_cached_forecast
from app.agriculture.models import AgriFarm
from app.agriculture.notification_dispatcher import AgriNotificationDispatcher
from app.database import async_session
from app.types.redis_client import RedisClient


async def check_weather(redis: RedisClient) -> int:
    sent = 0
    async with async_session() as db:
        farms = await db.scalars(select(AgriFarm))
        dispatcher = AgriNotificationDispatcher(db, redis)
        for farm in farms.all():
            if farm.location_lat is None or farm.location_lng is None:
                continue
            forecast = await get_cached_forecast(redis, float(farm.location_lat), float(farm.location_lng))
            if forecast.rain_next_hours(24):
                if await dispatcher.send_weather_warning(farm.id, "Hujan lebat"):
                    sent += 1
    return sent
