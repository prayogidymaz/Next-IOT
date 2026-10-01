import json
from datetime import UTC, datetime

from pydantic import JsonValue, TypeAdapter

from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient

LATEST_KEY_PREFIX = "device:telemetry:latest:"
_JSON_OBJECT = TypeAdapter(JsonObject)


def latest_cache_key(device_id: str) -> str:
    return f"{LATEST_KEY_PREFIX}{device_id}"


async def cache_latest_telemetry(
    redis: RedisClient,
    *,
    device_id: str,
    tenant_id: str,
    recorded_at: datetime,
    metrics: dict[str, JsonValue],
    reading_id: str,
) -> None:
    payload = {
        "reading_id": reading_id,
        "device_id": device_id,
        "tenant_id": tenant_id,
        "recorded_at": recorded_at.isoformat(),
        "metrics": metrics,
        "cached_at": datetime.now(UTC).isoformat(),
    }
    await redis.set(latest_cache_key(device_id), json.dumps(payload))


async def get_latest_telemetry(redis: RedisClient, device_id: str) -> JsonObject | None:
    raw = await redis.get(latest_cache_key(device_id))
    if raw is None:
        return None
    parsed: object = json.loads(raw)
    return _JSON_OBJECT.validate_python(parsed)
