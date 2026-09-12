"""SAR emergency alert broadcast via Redis pub/sub (WebSocket fan-out)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as aioredis

SAR_EMERGENCY_CHANNEL = "mission:sar:emergency:pubsub"


def sar_emergency_channel_for_tenant(tenant_id: str) -> str:
    return f"{SAR_EMERGENCY_CHANNEL}:{tenant_id}"


async def publish_sar_emergency_alert(
    redis: aioredis.Redis,
    *,
    tenant_id: str,
    event_type: str,
    incident: dict[str, Any],
) -> None:
    payload = {
        "event": event_type,
        "tenant_id": tenant_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "incident": incident,
    }
    encoded = json.dumps(payload, default=str)
    await redis.publish(sar_emergency_channel_for_tenant(tenant_id), encoded)
    await redis.publish(SAR_EMERGENCY_CHANNEL, encoded)
