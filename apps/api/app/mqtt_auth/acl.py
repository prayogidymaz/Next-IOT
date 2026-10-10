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


def _suffix_allows_command_response_publish(suffix: str) -> bool:
    if suffix == "commands/response":
        return True
    parts = suffix.split("/")
    if len(parts) == 3 and parts[0] == "commands" and parts[2] == "response":
        try:
            uuid.UUID(parts[1])
            return True
        except ValueError:
            return False
    return False


def _suffix_allows_command_subscribe(suffix: str) -> bool:
    if suffix == "commands/+/request":
        return True
    if suffix.startswith("commands/") and suffix != "commands/response":
        if suffix.count("/") == 1:
            return True
    return False


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
    }
    if normalized_action == "publish":
        if suffix in publish_allowed:
            return MqttAclDecision.ALLOW
        if _suffix_allows_command_response_publish(suffix):
            return MqttAclDecision.ALLOW
        return MqttAclDecision.DENY
    if normalized_action == "subscribe":
        if suffix == "attributes/shared/update":
            return MqttAclDecision.ALLOW
        if _suffix_allows_command_subscribe(suffix):
            return MqttAclDecision.ALLOW
        return MqttAclDecision.DENY
    return MqttAclDecision.DENY
