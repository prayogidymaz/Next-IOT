"""Rate limits for MQTT webhook endpoints (Redis sliding window)."""

from __future__ import annotations

import logging
import time

from app.types.redis_client import RedisClient
from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)

_MQTT_AUTH_LIMIT_PER_MINUTE = 6000
_MQTT_INGEST_LIMIT_PER_MINUTE = 60_000
_DEVICE_MSG_LIMIT_PER_SECOND = 10
_TENANT_MSG_LIMIT_PER_SECOND = 10_000


async def _sliding_window_count(redis: RedisClient, key: str, window_seconds: int) -> int:
    now = time.time()
    window_start = now - window_seconds
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {f"{now}": now})
    pipe.zcard(key)
    pipe.expire(key, window_seconds)
    results = await pipe.execute()
    return int(results[2])


async def enforce_mqtt_auth_rate_limit(redis: RedisClient, request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    key = f"ratelimit:mqtt:auth:{client_host}"
    count = await _sliding_window_count(redis, key, 60)
    if count > _MQTT_AUTH_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="MQTT auth rate limit exceeded")


async def enforce_mqtt_ingest_rate_limit(redis: RedisClient, request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    key = f"ratelimit:mqtt:ingest:{client_host}"
    count = await _sliding_window_count(redis, key, 60)
    if count > _MQTT_INGEST_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="MQTT ingest rate limit exceeded")


async def track_device_message_rates(
    redis: RedisClient,
    *,
    tenant_id: str,
    device_id: str,
) -> None:
    now = int(time.time())
    device_key = f"ratelimit:mqtt:device:{device_id}:{now}"
    tenant_key = f"ratelimit:mqtt:tenant:{tenant_id}:{now}"
    pipe = redis.pipeline()
    pipe.incr(device_key)
    pipe.expire(device_key, 2)
    pipe.incr(tenant_key)
    pipe.expire(tenant_key, 2)
    results = await pipe.execute()
    device_count = int(results[0])
    tenant_count = int(results[2])
    if device_count > _DEVICE_MSG_LIMIT_PER_SECOND:
        logger.warning("MQTT soft rate limit device %s (%s msg/s)", device_id, device_count)
    if tenant_count > _TENANT_MSG_LIMIT_PER_SECOND:
        logger.warning("MQTT soft rate limit tenant %s (%s msg/s)", tenant_id, tenant_count)
