import json
from datetime import UTC, datetime

from pydantic import JsonValue

from app.types.redis_client import RedisClient

DEVICE_EVENTS_QUEUE = "device:events"


async def emit_device_event(
    redis: RedisClient,
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
