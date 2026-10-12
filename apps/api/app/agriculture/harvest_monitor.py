"""Harvest reminder based on crop calendar."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select

from app.agriculture.models import AgriCropCalendar, AgriFarm
from app.agriculture.notification_dispatcher import AgriNotificationDispatcher
from app.database import async_session
from app.types.redis_client import RedisClient


async def check_harvest_reminders(redis: RedisClient) -> int:
    sent = 0
    now = datetime.now(tz=UTC)
    async with async_session() as db:
        farms = await db.scalars(select(AgriFarm))
        dispatcher = AgriNotificationDispatcher(db, redis)
        for farm in farms.all():
            stage = await db.scalar(
                select(AgriCropCalendar)
                .where(AgriCropCalendar.farm_id == farm.id, AgriCropCalendar.stage == "fruiting")
                .order_by(AgriCropCalendar.started_at.desc())
                .limit(1)
            )
            if stage is None or stage.expected_end_at is None:
                continue
            days_left = (stage.expected_end_at - now).days
            if 0 <= days_left <= 14:
                date_str = stage.expected_end_at.date().isoformat()
                if await dispatcher.send_harvest_reminder(farm.id, date_str):
                    sent += 1
    return sent
