"""Send notifications directly (without an alarm row)."""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.notification_gateway import NotificationChannel, NotificationLog
from app.notifications.providers.registry import provider_for
from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient


def _throttle_key(channel_id: uuid.UUID, fingerprint: str) -> str:
    return f"notif:throttle:{channel_id}:{fingerprint}"


async def send_direct_notification(
    db: AsyncSession,
    redis: RedisClient,
    *,
    tenant_id: uuid.UUID,
    channel_ids: list[uuid.UUID],
    title: str,
    message: str,
    severity: str,
    fingerprint: str,
) -> None:
    for channel_id in channel_ids:
        channel = await db.scalar(
            select(NotificationChannel).where(
                NotificationChannel.id == channel_id,
                NotificationChannel.tenant_id == tenant_id,
                NotificationChannel.is_active.is_(True),
            )
        )
        if channel is None:
            continue
        throttle_key = _throttle_key(channel.id, fingerprint)
        if int(await redis.exists(throttle_key)) > 0:
            continue

        log = NotificationLog(
            alarm_id=None,
            channel_id=channel.id,
            channel_type=channel.channel_type,
            status="pending",
        )
        db.add(log)
        await db.flush()

        config: JsonObject = {}
        for key, value in channel.config.items():
            if isinstance(key, str) and (
                isinstance(value, dict | list | str | int | float | bool) or value is None
            ):
                config[key] = value

        provider = provider_for(channel.channel_type)
        if provider is None:
            log.status = "failed"
            log.error_message = f"unknown channel type {channel.channel_type}"
            continue

        delay = settings.notification_retry_delay_seconds
        max_retries = settings.notification_max_retries
        last_error: str | None = None
        for attempt in range(1, max_retries + 1):
            try:
                result = await provider.send(config, title, message, severity)
                log.retry_count = attempt - 1
                if result.success:
                    log.status = "delivered" if result.delivered else "sent"
                    log.sent_at = datetime.now(UTC)
                    log.delivered_at = datetime.now(UTC) if result.delivered else None
                    if result.response is not None:
                        log.provider_response = dict(result.response)
                    await redis.setex(throttle_key, 60, "1")
                    break
                last_error = result.error
            except Exception as exc:
                last_error = str(exc)
            if attempt < max_retries:
                await asyncio.sleep(delay * attempt)
        else:
            log.status = "failed"
            log.error_message = last_error
            log.retry_count = max_retries
