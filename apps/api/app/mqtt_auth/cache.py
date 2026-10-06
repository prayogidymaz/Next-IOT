"""Redis cache for MQTT credential lookups."""

from __future__ import annotations

import json
import uuid

from app.config import settings
from app.types.redis_client import RedisClient

_CACHE_PREFIX = "mqtt:auth:"


class CachedMqttCredential:
    __slots__ = ("device_id", "tenant_id")

    def __init__(self, device_id: uuid.UUID, tenant_id: uuid.UUID) -> None:
        self.device_id = device_id
        self.tenant_id = tenant_id


def _cache_key(access_token: str) -> str:
    return f"{_CACHE_PREFIX}{access_token}"


async def get_cached_credential(redis: RedisClient, access_token: str) -> CachedMqttCredential | None:
    raw = await redis.get(_cache_key(access_token))
    if raw is None:
        return None
    payload = json.loads(raw)
    return CachedMqttCredential(
        device_id=uuid.UUID(payload["device_id"]),
        tenant_id=uuid.UUID(payload["tenant_id"]),
    )


async def set_cached_credential(
    redis: RedisClient,
    access_token: str,
    *,
    device_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> None:
    payload = json.dumps({"device_id": str(device_id), "tenant_id": str(tenant_id)})
    await redis.setex(_cache_key(access_token), settings.mqtt_auth_cache_ttl_seconds, payload)


async def invalidate_cached_credential(redis: RedisClient, access_token: str) -> None:
    await redis.delete(_cache_key(access_token))
