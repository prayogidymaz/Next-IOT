"""Platform MQTT subscriber credentials (env-based, not device tokens)."""

from __future__ import annotations

import secrets

from app.config import settings
from app.mqtt_auth.acl import MqttAclDecision
from app.mqtt_auth.schemas import MqttAclRequest, MqttAuthRequest

SUBSCRIBER_TELEMETRY_FILTER = "tenants/+/devices/+/telemetry"
SUBSCRIBER_TELEMETRY_SHARE_FILTER = "$share/nextiot-ingest/tenants/+/devices/+/telemetry"

_SUBSCRIBER_SUBSCRIBE_TOPICS = frozenset(
    {
        SUBSCRIBER_TELEMETRY_FILTER,
        SUBSCRIBER_TELEMETRY_SHARE_FILTER,
    }
)


def is_platform_subscriber_auth(payload: MqttAuthRequest) -> bool:
    if not settings.mqtt_subscriber_enabled:
        return False
    username = payload.username.strip() or payload.clientid.strip()
    password = payload.password
    expected_user = settings.mqtt_subscriber_internal_user
    expected_password = settings.mqtt_subscriber_internal_password
    return secrets.compare_digest(username, expected_user) and secrets.compare_digest(
        password,
        expected_password,
    )


def is_platform_subscriber_acl_request(payload: MqttAclRequest) -> bool:
    if not settings.mqtt_subscriber_enabled:
        return False
    username = payload.username.strip() or payload.clientid.strip()
    return secrets.compare_digest(username, settings.mqtt_subscriber_internal_user)


def evaluate_platform_subscriber_acl(topic: str, action: str) -> MqttAclDecision:
    normalized_action = action.lower()
    if normalized_action == "publish":
        return MqttAclDecision.DENY
    if normalized_action != "subscribe":
        return MqttAclDecision.DENY
    if topic in _SUBSCRIBER_SUBSCRIBE_TOPICS:
        return MqttAclDecision.ALLOW
    return MqttAclDecision.DENY
