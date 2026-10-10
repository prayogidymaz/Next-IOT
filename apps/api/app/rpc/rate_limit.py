"""Per-device RPC rate limiting."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status

from app.config import settings
from app.types.redis_client import RedisClient


def _rpc_rate_key(device_id: uuid.UUID) -> str:
    return f"rpc:rate:{device_id}"


async def enforce_rpc_rate_limit(redis: RedisClient, device_id: uuid.UUID) -> None:
    key = _rpc_rate_key(device_id)
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 60)
    if count > settings.rpc_rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="RPC rate limit exceeded for this device",
        )
