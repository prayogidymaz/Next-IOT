import json
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as aioredis

MAVLINK_STATUS_KEY_PREFIX = "hardware:mavlink:status:"


def mavlink_status_key(device_id: str) -> str:
    return f"{MAVLINK_STATUS_KEY_PREFIX}{device_id}"


async def save_mavlink_status(
    redis: aioredis.Redis,
    *,
    device_id: str,
    snapshot: dict[str, Any],
) -> None:
    payload = {
        **snapshot,
        "device_id": device_id,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    await redis.set(mavlink_status_key(device_id), json.dumps(payload), ex=120)


async def read_mavlink_status(redis: aioredis.Redis, device_id: str) -> dict[str, Any]:
    raw = await redis.get(mavlink_status_key(device_id))
    if raw is None:
        return {
            "device_id": device_id,
            "connected": False,
            "protocol_version": "2.0",
            "metrics": {},
        }
    data = json.loads(raw)
    data.setdefault("connected", bool(data.get("mavlink_connected")))
    return data
