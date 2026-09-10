import redis.asyncio as aioredis

from app.config import settings

LIVENESS_KEY_PREFIX = "device:liveness:"


def _ttl_seconds() -> int:
    return settings.device_heartbeat_offline_threshold_seconds


def liveness_key(device_id: str) -> str:
    return f"{LIVENESS_KEY_PREFIX}{device_id}"


async def touch_liveness(redis: aioredis.Redis, device_id: str) -> None:
    await redis.set(liveness_key(device_id), "1", ex=_ttl_seconds())


async def is_lively(redis: aioredis.Redis, device_id: str) -> bool:
    return await redis.exists(liveness_key(device_id)) == 1


async def clear_liveness(redis: aioredis.Redis, device_id: str) -> None:
    await redis.delete(liveness_key(device_id))
