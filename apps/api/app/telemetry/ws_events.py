"""Control Center live stream events (Redis pub/sub)."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import redis.asyncio as aioredis
from pydantic import JsonValue

TELEMETRY_WS_CHANNEL_PREFIX = "telemetry:tenant:"


def telemetry_channel_for_tenant(tenant_id: str) -> str:
    return f"{TELEMETRY_WS_CHANNEL_PREFIX}{tenant_id}"


async def publish_control_center_event(
    redis: aioredis.Redis,
    *,
    tenant_id: str,
    event_type: str,
    payload: dict[str, JsonValue],
) -> None:
    message = {
        "type": event_type,
        "tenant_id": tenant_id,
        "timestamp": datetime.now(UTC).isoformat(),
        **payload,
    }
    await redis.publish(telemetry_channel_for_tenant(tenant_id), json.dumps(message, default=str))
