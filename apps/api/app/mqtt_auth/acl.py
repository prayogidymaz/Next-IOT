"""Parse and evaluate MQTT topic ACL rules (pure, no I/O)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import StrEnum


class MqttAclDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class ParsedDeviceTopic:
    tenant_id: uuid.UUID
    device_id: uuid.UUID
    suffix: str


def parse_device_topic(topic: str) -> ParsedDeviceTopic | None:
    parts = topic.strip("/").split("/")
    if len(parts) < 4:
        return None
    if parts[0] != "tenants" or parts[2] != "devices":
        return None
    try:
        tenant_id = uuid.UUID(parts[1])
        device_id = uuid.UUID(parts[3])
    except ValueError:
        return None
    suffix = "/".join(parts[4:])
    return ParsedDeviceTopic(tenant_id=tenant_id, device_id=device_id, suffix=suffix)


def evaluate_device_acl(
    *,
    credential_tenant_id: uuid.UUID,
    credential_device_id: uuid.UUID,
    topic: str,
    action: str,
) -> MqttAclDecision:
    parsed = parse_device_topic(topic)
    if parsed is None:
        return MqttAclDecision.DENY
    if parsed.tenant_id != credential_tenant_id or parsed.device_id != credential_device_id:
        return MqttAclDecision.DENY

    normalized_action = action.lower()
    suffix = parsed.suffix

    publish_allowed = {
        "telemetry",
        "attributes",
        "commands/response",
    }
    if normalized_action == "publish":
        return MqttAclDecision.ALLOW if suffix in publish_allowed else MqttAclDecision.DENY
    if normalized_action == "subscribe":
        if suffix == "attributes/shared":
            return MqttAclDecision.ALLOW
        if suffix.startswith("commands/") and suffix != "commands/response":
            return MqttAclDecision.ALLOW
        return MqttAclDecision.DENY
    return MqttAclDecision.DENY
