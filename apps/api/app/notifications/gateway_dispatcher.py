"""Dispatch alarm notifications to configured channels."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.models.alarm import Alarm, AlarmStatus
from app.models.notification_gateway import NotificationChannel, NotificationLog, NotificationRule
from app.notifications.providers.registry import provider_for
from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient, close_redis, redis_from_url

logger = logging.getLogger(__name__)


def _throttle_key(channel_id: uuid.UUID, fingerprint: str) -> str:
    return f"notif:throttle:{channel_id}:{fingerprint}"


def alarm_matches_filter(alarm: Alarm, alarm_filter: dict[str, object]) -> bool:
    severities_raw = alarm_filter.get("severity")
    if isinstance(severities_raw, list):
        allowed = {s for s in severities_raw if isinstance(s, str)}
        if allowed and alarm.severity not in allowed:
            return False
    device_raw = alarm_filter.get("device_id")
    if isinstance(device_raw, str):
        try:
            if alarm.device_id != uuid.UUID(device_raw):
                return False
        except ValueError:
            return False
    type_raw = alarm_filter.get("alarm_type")
    if isinstance(type_raw, str) and alarm.alarm_type != type_raw:
        return False
    return True


async def _is_throttled(redis: RedisClient, channel_id: uuid.UUID, fingerprint: str) -> bool:
    key = _throttle_key(channel_id, fingerprint)
    exists = await redis.exists(key)
    return int(exists) > 0


async def _mark_throttle(redis: RedisClient, channel_id: uuid.UUID, fingerprint: str, seconds: int) -> None:
    key = _throttle_key(channel_id, fingerprint)
    await redis.setex(key, seconds, "1")


async def _send_with_retry(
    db: AsyncSession,
    *,
    alarm: Alarm,
    channel: NotificationChannel,
    throttle_seconds: int,
    redis: RedisClient,
) -> None:
    if await _is_throttled(redis, channel.id, alarm.fingerprint):
        return
    provider = provider_for(channel.channel_type)
    log = NotificationLog(
        alarm_id=alarm.id,
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

    if provider is None:
        log.status = "failed"
        log.error_message = f"unknown channel type {channel.channel_type}"
        return

    delay = settings.notification_retry_delay_seconds
    max_retries = settings.notification_max_retries
    last_error: str | None = None
    for attempt in range(1, max_retries + 1):
        try:
            result = await provider.send(
                config,
                alarm.title,
                alarm.message or "",
                alarm.severity,
            )
            log.retry_count = attempt - 1
            if result.success:
                log.status = "delivered" if result.delivered else "sent"
                log.sent_at = datetime.now(UTC)
                log.delivered_at = datetime.now(UTC) if result.delivered else None
                if result.response is not None:
                    log.provider_response = dict(result.response)
                await _mark_throttle(redis, channel.id, alarm.fingerprint, throttle_seconds)
                return
            last_error = result.error
        except Exception as exc:
            last_error = str(exc)
        if attempt < max_retries:
            await asyncio.sleep(delay * attempt)
    log.status = "failed"
    log.error_message = last_error
    log.retry_count = max_retries


async def dispatch_alarm_notifications(
    db: AsyncSession,
    redis: RedisClient,
    alarm_id: uuid.UUID,
) -> None:
    alarm = await db.scalar(select(Alarm).where(Alarm.id == alarm_id))
    if alarm is None:
        return
    rules = list(
        await db.scalars(
            select(NotificationRule).where(
                NotificationRule.tenant_id == alarm.tenant_id,
                NotificationRule.is_active.is_(True),
            )
        )
    )
    for rule in rules:
        if not alarm_matches_filter(alarm, rule.alarm_filter):
            continue
        for channel_id in rule.channel_ids:
            channel = await db.scalar(
                select(NotificationChannel).where(
                    NotificationChannel.id == channel_id,
                    NotificationChannel.is_active.is_(True),
                )
            )
            if channel is None:
                continue
            await _send_with_retry(
                db,
                alarm=alarm,
                channel=channel,
                throttle_seconds=rule.throttle_seconds,
                redis=redis,
            )


async def dispatch_alarm_notifications_task(alarm_id: uuid.UUID) -> None:
    import os

    redis_url = settings.redis_url_for_tests() if os.environ.get("TESTING") == "1" else settings.redis_url
    redis = redis_from_url(redis_url)
    try:
        async with async_session() as db:
            await dispatch_alarm_notifications(db, redis, alarm_id)
            await db.commit()
    except Exception:
        logger.exception("Alarm notification dispatch failed for %s", alarm_id)
    finally:
        await close_redis(redis)


async def run_escalation_resend_once(redis: RedisClient) -> None:
    now = datetime.now(UTC)
    async with async_session() as db:
        rules = list(
            await db.scalars(
                select(NotificationRule).where(
                    NotificationRule.is_active.is_(True),
                    NotificationRule.escalation_minutes.is_not(None),
                )
            )
        )
        for rule in rules:
            minutes = rule.escalation_minutes
            if minutes is None:
                continue
            cutoff = now - timedelta(minutes=minutes)
            alarms = list(
                await db.scalars(
                    select(Alarm).where(
                        Alarm.tenant_id == rule.tenant_id,
                        Alarm.status == AlarmStatus.ACTIVE,
                        Alarm.occurred_at <= cutoff,
                    )
                )
            )
            for alarm in alarms:
                if not alarm_matches_filter(alarm, rule.alarm_filter):
                    continue
                for channel_id in rule.channel_ids:
                    channel = await db.scalar(
                        select(NotificationChannel).where(NotificationChannel.id == channel_id)
                    )
                    if channel is None:
                        continue
                    await _send_with_retry(
                        db,
                        alarm=alarm,
                        channel=channel,
                        throttle_seconds=rule.throttle_seconds,
                        redis=redis,
                    )
        await db.commit()
