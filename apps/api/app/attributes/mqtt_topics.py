"""MQTT topic helpers for device attributes."""

from __future__ import annotations

import uuid

from app.mqtt_auth.acl import parse_device_topic


def client_attributes_topic(tenant_id: uuid.UUID, device_id: uuid.UUID) -> str:
    return f"tenants/{tenant_id}/devices/{device_id}/attributes"


def shared_attribute_update_topic(tenant_id: uuid.UUID, device_id: uuid.UUID) -> str:
    return f"tenants/{tenant_id}/devices/{device_id}/attributes/shared/update"


def parse_client_attributes_topic(topic: str) -> tuple[uuid.UUID, uuid.UUID] | None:
    parsed = parse_device_topic(topic)
    if parsed is None or parsed.suffix != "attributes":
        return None
    return parsed.tenant_id, parsed.device_id
