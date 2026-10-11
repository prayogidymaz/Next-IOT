"""Redis-backed quota counters and enforcement."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.limits import PlanLimits, parse_plan_limits
from app.billing.subscription_service import get_tenant_limits
from app.models.device import Device
from app.types.redis_client import RedisClient


def _month_key(tenant_id: uuid.UUID) -> str:
    now = datetime.now(tz=UTC)
    return f"quota:msg:{tenant_id}:{now.year}-{now.month:02d}"


def _day_key(tenant_id: uuid.UUID) -> str:
    now = datetime.now(tz=UTC)
    return f"quota:api:{tenant_id}:{now.date().isoformat()}"


async def increment_message_count(redis: RedisClient, tenant_id: uuid.UUID, amount: int = 1) -> int:
    key = _month_key(tenant_id)
    new_val = await redis.incrby(key, amount)
    if new_val == amount:
        await redis.expire(key, 60 * 60 * 24 * 35)
    return int(new_val)


async def get_message_count(redis: RedisClient, tenant_id: uuid.UUID) -> int:
    raw = await redis.get(_month_key(tenant_id))
    if raw is None:
        return 0
    try:
        return int(raw)
    except ValueError:
        return 0


async def increment_api_call(redis: RedisClient, tenant_id: uuid.UUID) -> int:
    key = _day_key(tenant_id)
    new_val = await redis.incr(key)
    if new_val == 1:
        await redis.expire(key, 60 * 60 * 26)
    return int(new_val)


def _quota_exceeded(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=detail,
    )


async def assert_device_quota(db: AsyncSession, tenant_id: uuid.UUID) -> None:
    limits: PlanLimits = await get_tenant_limits(db, tenant_id)
    if limits.max_devices is None:
        return
    count = await db.scalar(select(func.count()).select_from(Device).where(Device.tenant_id == tenant_id))
    device_count = int(count or 0)
    if device_count >= limits.max_devices:
        raise _quota_exceeded(
            f"Device limit reached ({device_count}/{limits.max_devices}). Upgrade your subscription plan."
        )


async def assert_message_quota(db: AsyncSession, redis: RedisClient, tenant_id: uuid.UUID) -> None:
    limits: PlanLimits = await get_tenant_limits(db, tenant_id)
    if limits.max_messages_per_month is None:
        return
    used = await get_message_count(redis, tenant_id)
    if used >= limits.max_messages_per_month:
        raise _quota_exceeded(
            f"Monthly message quota exceeded ({used}/{limits.max_messages_per_month})."
        )


async def assert_api_quota(db: AsyncSession, redis: RedisClient, tenant_id: uuid.UUID) -> None:
    limits: PlanLimits = await get_tenant_limits(db, tenant_id)
    if limits.max_api_calls_per_day is None:
        return
    raw = await redis.get(_day_key(tenant_id))
    used = int(raw) if raw is not None else 0
    if used > limits.max_api_calls_per_day:
        raise _quota_exceeded(
            f"Daily API call quota exceeded ({used}/{limits.max_api_calls_per_day})."
        )


def limits_from_plan_json(limits_json: dict[str, object]) -> PlanLimits:
    return parse_plan_limits(limits_json)
