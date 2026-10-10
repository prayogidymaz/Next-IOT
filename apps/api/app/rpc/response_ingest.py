"""Handle device RPC responses from MQTT subscriber."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device_rpc_request import DeviceRpcRequest, DeviceRpcStatus
from app.rpc.event_registry import RpcWaitResult, rpc_event_registry
from app.rpc.mqtt_topics import ParsedRpcResponseTopic


def _response_payload_value(payload: dict[str, JsonValue]) -> JsonValue | None:
    if "data" in payload:
        return payload.get("data")
    return payload


async def handle_rpc_response_from_mqtt(
    db: AsyncSession,
    topic: ParsedRpcResponseTopic,
    payload: dict[str, JsonValue],
) -> bool:
    row = await db.scalar(
        select(DeviceRpcRequest).where(
            DeviceRpcRequest.id == topic.request_id,
            DeviceRpcRequest.device_id == topic.device_id,
            DeviceRpcRequest.tenant_id == topic.tenant_id,
        )
    )
    if row is None:
        return False
    if row.status in {DeviceRpcStatus.COMPLETED, DeviceRpcStatus.TIMEOUT, DeviceRpcStatus.FAILED}:
        return False

    status_raw = payload.get("status")
    status_text = status_raw if isinstance(status_raw, str) else "ok"
    error_raw = payload.get("error")
    error_text = error_raw if isinstance(error_raw, str) else None
    response_value = _response_payload_value(payload)

    if status_text == "error":
        row.status = DeviceRpcStatus.FAILED
        row.error_message = error_text or "device reported error"
        row.response_json = None
    else:
        row.status = DeviceRpcStatus.COMPLETED
        if isinstance(response_value, dict):
            stored: dict[str, object] = {}
            for key, val in response_value.items():
                if isinstance(key, str):
                    stored[key] = val
            row.response_json = stored
        elif response_value is None:
            row.response_json = {}
        else:
            row.response_json = {"data": response_value}
        row.error_message = None
    row.completed_at = datetime.now(UTC)
    await db.flush()

    rpc_event_registry.resolve(
        topic.request_id,
        RpcWaitResult(status=row.status, response=response_value, error=row.error_message),
    )
    return True
