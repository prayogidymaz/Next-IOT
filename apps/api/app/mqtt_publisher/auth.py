"""Platform MQTT publisher credentials (publish-only internal user)."""

from __future__ import annotations

import secrets
import uuid

from app.config import settings
from app.mqtt_auth.acl import MqttAclDecision, parse_device_topic
from app.mqtt_auth.schemas import MqttAclRequest, MqttAuthRequest


def is_platform_publisher_auth(payload: MqttAuthRequest) -> bool:
    if not settings.mqtt_publisher_enabled:
        return False
    username = payload.username.strip() or payload.clientid.strip()
    password = payload.password
    return secrets.compare_digest(username, settings.mqtt_publisher_internal_user) and secrets.compare_digest(
        password,
        settings.mqtt_publisher_internal_password,
    )


def is_platform_publisher_acl_request(payload: MqttAclRequest) -> bool:
    if not settings.mqtt_publisher_enabled:
        return False
    username = payload.username.strip() or payload.clientid.strip()
    return secrets.compare_digest(username, settings.mqtt_publisher_internal_user)


def _suffix_allows_publisher_publish(suffix: str) -> bool:
    if suffix == "attributes/shared/update":
        return True
    parts = suffix.split("/")
    if len(parts) == 3 and parts[0] == "commands" and parts[2] == "request":
        try:
            uuid.UUID(parts[1])
            return True
        except ValueError:
            return False
    return False


def evaluate_platform_publisher_acl(topic: str, action: str) -> MqttAclDecision:
    normalized = action.lower()
    if normalized != "publish":
        return MqttAclDecision.DENY
    parsed = parse_device_topic(topic)
    if parsed is None:
        return MqttAclDecision.DENY
    if _suffix_allows_publisher_publish(parsed.suffix):
        return MqttAclDecision.ALLOW
    return MqttAclDecision.DENY
