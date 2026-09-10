import json
from typing import Any

import redis.asyncio as aioredis

from app.devices.events import emit_device_event

DEVICE_COMMANDS_CHANNEL = "device:commands:pubsub"


async def publish_device_command(
    redis: aioredis.Redis,
    *,
    command_id: str,
    device_id: str,
    tenant_id: str,
    command_type: str,
    params: dict[str, Any],
    issued_by_user_id: str | None,
) -> None:
    payload = {
        "command_id": command_id,
        "device_id": device_id,
        "tenant_id": tenant_id,
        "command_type": command_type,
        "params": params,
        "issued_by_user_id": issued_by_user_id,
    }
    await redis.publish(DEVICE_COMMANDS_CHANNEL, json.dumps(payload))
    await emit_device_event(
        redis,
        "command.dispatched",
        device_id=device_id,
        tenant_id=tenant_id,
        extra={
            "command_id": command_id,
            "command_type": command_type,
            "params": params,
        },
    )
