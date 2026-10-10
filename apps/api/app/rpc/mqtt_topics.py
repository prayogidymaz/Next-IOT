"""MQTT topic helpers for device RPC."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.mqtt_auth.acl import parse_device_topic


def rpc_request_topic(tenant_id: uuid.UUID, device_id: uuid.UUID, request_id: uuid.UUID) -> str:
    return f"tenants/{tenant_id}/devices/{device_id}/commands/{request_id}/request"


@dataclass(frozen=True)
class ParsedRpcResponseTopic:
    tenant_id: uuid.UUID
    device_id: uuid.UUID
    request_id: uuid.UUID


def parse_rpc_response_topic(topic: str) -> ParsedRpcResponseTopic | None:
    parsed = parse_device_topic(topic)
    if parsed is None:
        return None
    parts = parsed.suffix.split("/")
    if len(parts) != 3 or parts[0] != "commands" or parts[2] != "response":
        return None
    try:
        request_id = uuid.UUID(parts[1])
    except ValueError:
        return None
    return ParsedRpcResponseTopic(
        tenant_id=parsed.tenant_id,
        device_id=parsed.device_id,
        request_id=request_id,
    )
