"""Broadcast shared attribute updates to devices over MQTT."""

from __future__ import annotations

import uuid

from pydantic import JsonValue

from app.attributes.mqtt_topics import shared_attribute_update_topic
from app.mqtt_publisher.protocol import MqttPublisherProtocol


async def broadcast_shared_attribute_update(
    publisher: MqttPublisherProtocol,
    *,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID,
    key: str,
    value: JsonValue,
    qos: int,
) -> None:
    topic = shared_attribute_update_topic(tenant_id, device_id)
    await publisher.publish_json(topic, {key: value}, qos=qos)
