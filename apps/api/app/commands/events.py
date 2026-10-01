import json

from pydantic import JsonValue

from app.devices.events import emit_device_event
from app.types.redis_client import RedisClient

DEVICE_COMMANDS_CHANNEL = "device:commands:pubsub"
HARDWARE_MQTT_BRIDGE_CHANNEL = "hardware:mqtt:commands"


async def publish_device_command(
    redis: RedisClient,
    *,
    command_id: str,
    device_id: str,
    tenant_id: str,
    command_type: str,
    params: dict[str, JsonValue],
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
    mqtt_envelope = {
        "topic": f"next-iot/{tenant_id}/devices/{device_id}/command",
        "qos": 1,
        "retain": False,
        "payload": {
            "command_id": command_id,
            "command_type": command_type,
            "params": params,
        },
    }
    await redis.publish(HARDWARE_MQTT_BRIDGE_CHANNEL, json.dumps(mqtt_envelope))
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
