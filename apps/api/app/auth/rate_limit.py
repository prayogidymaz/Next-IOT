import time

import redis.asyncio as aioredis
from fastapi import HTTPException, status

from app.auth.tiering import SecurityTier, rate_limit_for_tier

RATE_LIMIT_WINDOW_SECONDS = 60
RATE_KEY_PREFIX = "ratelimit:"


async def enforce_rate_limit(
    redis: aioredis.Redis,
    *,
    tenant_id: str,
    user_id: str,
    security_tier: SecurityTier,
) -> None:
    limit = rate_limit_for_tier(security_tier)
    key = f"{RATE_KEY_PREFIX}{tenant_id}:{user_id}"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {f"{now}": now})
    pipe.zcard(key)
    pipe.expire(key, RATE_LIMIT_WINDOW_SECONDS)
    results = await pipe.execute()
    request_count = results[2]

    if request_count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for tier '{security_tier.value}' ({limit} req/min)",
        )
