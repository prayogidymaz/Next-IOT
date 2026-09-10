import asyncio
import json
import logging

import redis.asyncio as aioredis

from app.config import settings
from app.notifications.dispatcher import NotificationDispatcher
from app.rules.alerts import ALERTS_QUEUE

logger = logging.getLogger(__name__)


async def process_alert_queue_once(
    redis: aioredis.Redis,
    dispatcher: NotificationDispatcher | None = None,
) -> int:
    """Process up to one alert from the Redis queue. Returns count dispatched."""
    active_dispatcher = dispatcher or NotificationDispatcher()
    raw = await redis.rpop(ALERTS_QUEUE)
    if raw is None:
        return 0

    try:
        alert = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Skipping malformed alert payload: %s", raw[:200])
        return 0

    results = await active_dispatcher.dispatch(alert)
    for result in results:
        if result.success:
            logger.info("Alert dispatched via %s (attempts=%d)", result.provider, result.attempts)
        else:
            logger.warning(
                "Alert dispatch failed via %s (attempts=%d): %s",
                result.provider,
                result.attempts,
                result.error,
            )
    return 1


async def notification_dispatcher_loop(
    redis: aioredis.Redis,
    stop_event: asyncio.Event,
) -> None:
    """Background consumer for device:alerts Redis queue."""
    if not settings.notification_dispatcher_enabled:
        logger.info("Notification dispatcher worker disabled")
        return

    dispatcher = NotificationDispatcher()
    poll = settings.notification_poll_interval_seconds
    logger.info("Notification dispatcher worker started (queue=%s)", ALERTS_QUEUE)

    while not stop_event.is_set():
        try:
            processed = await process_alert_queue_once(redis, dispatcher)
            if processed == 0:
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=poll)
                except asyncio.TimeoutError:
                    continue
        except Exception:
            logger.exception("Notification dispatcher iteration failed")
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=poll)
            except asyncio.TimeoutError:
                continue
