import json
from datetime import UTC, datetime

import redis.asyncio as aioredis
from pydantic import JsonValue

DEVICE_EVENTS_QUEUE = "device:events"


async def emit_device_event(
    redis: aioredis.Redis,
    event_type: str,
    *,
    device_id: str,
    tenant_id: str,
    extra: dict[str, JsonValue] | None = None,
) -> None:
    payload = {
        "event": event_type,
        "device_id": device_id,
        "tenant_id": tenant_id,
        "timestamp": datetime.now(UTC).isoformat(),
        **(extra or {}),
    }
    await redis.lpush(DEVICE_EVENTS_QUEUE, json.dumps(payload))
