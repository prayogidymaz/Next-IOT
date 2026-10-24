"""Publish Universal Mesh motion events from the drone simulator."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

import aiomqtt
from pydantic import JsonValue

from app.config import settings
from app.mesh.event_bus import MeshDomain, mesh_event_topic
from app.models.device import Device

logger = logging.getLogger(__name__)


async def publish_drone_mesh_event(
    device: Device,
    event_type: str,
    payload: dict[str, JsonValue],
) -> None:
    event_id = uuid.uuid4()
    envelope: dict[str, JsonValue] = {
        "event_id": str(event_id),
        "tenant_id": str(device.tenant_id),
        "device_id": str(device.id),
        "domain": MeshDomain.MOTION.value,
        "event_type": event_type,
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "payload": payload,
        "context": {},
        "correlation_id": None,
        "parent_event_id": None,
    }
    topic = mesh_event_topic(str(device.tenant_id), MeshDomain.MOTION, event_type)
    try:
        async with aiomqtt.Client(
            hostname=settings.mqtt_broker_host,
            port=settings.mqtt_broker_port,
            username=settings.mqtt_publisher_internal_user or None,
            password=settings.mqtt_publisher_internal_password or None,
        ) as client:
            await client.publish(topic, json.dumps(envelope))
    except Exception:
        logger.exception("Drone mesh MQTT publish failed event_type=%s", event_type)
