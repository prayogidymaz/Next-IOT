"""Fire-and-forget RPC publish (no response wait)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import JsonValue
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.device_rpc_request import DeviceRpcRequest, DeviceRpcStatus
from app.mqtt_publisher.protocol import MqttPublisherProtocol
from app.rpc.mqtt_topics import rpc_request_topic
from app.types.json_types import JsonObject


def _json_object(params: dict[str, JsonValue]) -> JsonObject:
    out: JsonObject = {}
    for key, value in params.items():
        if isinstance(key, str) and (
            isinstance(value, dict | list | str | int | float | bool) or value is None
        ):
            out[key] = value
    return out


async def publish_rpc_fire_and_forget(
    db: AsyncSession,
    publisher: MqttPublisherProtocol,
    *,
    device: Device,
    method: str,
    params: dict[str, JsonValue],
    timeout_seconds: int,
) -> uuid.UUID:
    row = DeviceRpcRequest(
        device_id=device.id,
        tenant_id=device.tenant_id,
        method=method,
        params=_json_object(params),
        status=DeviceRpcStatus.PENDING,
        timeout_seconds=timeout_seconds,
        requested_by_user_id=None,
    )
    db.add(row)
    await db.flush()
    topic = rpc_request_topic(device.tenant_id, device.id, row.id)
    await publisher.publish_json(
        topic,
        {"method": method, "params": params, "request_id": str(row.id)},
        qos=1,
    )
    row.status = DeviceRpcStatus.DELIVERED
    row.delivered_at = datetime.now(UTC)
    await db.flush()
    return row.id
