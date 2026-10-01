from app.config import settings
from app.types.redis_client import RedisClient

LIVENESS_KEY_PREFIX = "device:liveness:"


def _ttl_seconds() -> int:
    return settings.device_heartbeat_offline_threshold_seconds


def liveness_key(device_id: str) -> str:
    return f"{LIVENESS_KEY_PREFIX}{device_id}"


async def touch_liveness(redis: RedisClient, device_id: str) -> None:
    await redis.set(liveness_key(device_id), "1", ex=_ttl_seconds())


async def is_lively(redis: RedisClient, device_id: str) -> bool:
    exists = await redis.exists(liveness_key(device_id))
    return bool(exists == 1)


async def clear_liveness(redis: RedisClient, device_id: str) -> None:
    await redis.delete(liveness_key(device_id))
