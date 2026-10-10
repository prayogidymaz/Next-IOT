"""FastAPI dependency for MQTT publisher."""

from __future__ import annotations

from typing import cast

from fastapi import HTTPException, Request, status

from app.mqtt_publisher.noop import NoopMqttPublisher
from app.mqtt_publisher.protocol import MqttPublisherProtocol
from app.mqtt_publisher.service import MqttPublisherService


def get_mqtt_publisher(request: Request) -> MqttPublisherProtocol:
    publisher: object = getattr(request.app.state, "mqtt_publisher", None)
    if publisher is None:
        return NoopMqttPublisher()
    if isinstance(publisher, MqttPublisherService | NoopMqttPublisher):
        return publisher
    if callable(getattr(publisher, "publish_json", None)):
        # Test doubles and mocks implement publish_json; Protocol is structural.
        return cast(MqttPublisherProtocol, publisher)
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MQTT publisher unavailable")
