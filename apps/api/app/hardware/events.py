import json
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as aioredis

from app.config import settings

LORA_TELEMETRY_CHANNEL = "hardware:lora:telemetry"
GATEWAY_STATUS_KEY = "hardware:gateway:status"


async def publish_lora_telemetry(redis: aioredis.Redis, payload: dict[str, Any]) -> None:
    await redis.publish(LORA_TELEMETRY_CHANNEL, json.dumps(payload))


async def update_gateway_status(redis: aioredis.Redis, status: dict[str, Any]) -> None:
    enriched = {
        **status,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    await redis.set(GATEWAY_STATUS_KEY, json.dumps(enriched), ex=settings.lora_gateway_status_ttl_seconds)


async def get_gateway_status(redis: aioredis.Redis) -> dict[str, Any] | None:
    raw = await redis.get(GATEWAY_STATUS_KEY)
    if raw is None:
        return None
    return json.loads(raw)
