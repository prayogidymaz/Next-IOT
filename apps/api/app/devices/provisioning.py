import redis.asyncio as aioredis

from app.config import settings
from app.devices.security import hash_provisioning_token

PROVISION_KEY_PREFIX = "provision:"


def _ttl_seconds() -> int:
    return settings.device_provisioning_token_expire_hours * 3600


async def store_provisioning_token(redis: aioredis.Redis, token: str, device_id: str) -> None:
    key = f"{PROVISION_KEY_PREFIX}{hash_provisioning_token(token)}"
    await redis.set(key, device_id, ex=_ttl_seconds())


async def consume_provisioning_token(redis: aioredis.Redis, token: str) -> str | None:
    key = f"{PROVISION_KEY_PREFIX}{hash_provisioning_token(token)}"
    device_id = await redis.get(key)
    if device_id is None:
        return None
    await redis.delete(key)
    return device_id
