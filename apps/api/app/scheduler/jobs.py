"""Scheduled agriculture background jobs."""

from __future__ import annotations

import logging

from app.agriculture.battery_monitor import check_batteries
from app.agriculture.harvest_monitor import check_harvest_reminders
from app.agriculture.weather_monitor import check_weather
from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)


async def disease_prediction_job(redis: RedisClient) -> int:
    from app.agriculture.worker import run_disease_scan_once

    created = await run_disease_scan_once(redis)
    if created:
        logger.info("disease_prediction_job created %s alerts", created)
    return created


async def battery_check_job(redis: RedisClient) -> int:
    count = await check_batteries(redis)
    if count:
        logger.info("battery_check_job sent %s warnings", count)
    return count


async def weather_check_job(redis: RedisClient) -> int:
    count = await check_weather(redis)
    if count:
        logger.info("weather_check_job sent %s warnings", count)
    return count


async def harvest_reminder_job(redis: RedisClient) -> int:
    count = await check_harvest_reminders(redis)
    if count:
        logger.info("harvest_reminder_job sent %s reminders", count)
    return count
