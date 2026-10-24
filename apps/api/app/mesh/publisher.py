"""Mesh event publisher — MQTT + persistence + Redis fan-out."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mesh.context_resolver import resolve_device_context
from app.mesh.event_bus import (
    MeshDomain,
    mesh_event_topic,
    mesh_tenant_fanout_channel,
    validate_domain_event_type,
)
from app.mesh.schemas import MeshContext, MeshEvent
from app.models.device import Device
from app.models.mesh_event import MeshEventRecord
from app.mqtt_publisher.protocol import MqttPublisherProtocol
from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)

_mesh_publisher: MeshEventPublisher | None = None


class MeshEventPublisher:
    def __init__(self, redis: RedisClient, mqtt: MqttPublisherProtocol) -> None:
        self._redis = redis
        self._mqtt = mqtt

    async def publish_event(
        self,
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        domain: MeshDomain,
        event_type: str,
        device_id: uuid.UUID,
        payload: JsonObject,
        context: MeshContext | None = None,
        correlation_id: uuid.UUID | None = None,
        parent_event_id: uuid.UUID | None = None,
        timestamp: datetime | None = None,
    ) -> uuid.UUID:
        if not validate_domain_event_type(domain, event_type):
            raise ValueError(f"Invalid event_type '{event_type}' for domain '{domain.value}'")

        device = await db.scalar(select(Device).where(Device.id == device_id))
        if device is None:
            raise ValueError("device not found")
        if device.tenant_id != tenant_id:
            raise ValueError("device tenant mismatch")

        resolved = context or await resolve_device_context(db, self._redis, device_id)
        event_id = uuid.uuid4()
        ts = timestamp or datetime.now(tz=UTC)
        context_store: dict[str, object] = resolved.model_dump(mode="json")

        row = MeshEventRecord(
            id=event_id,
            tenant_id=tenant_id,
            device_id=device_id,
            domain=domain.value,
            event_type=event_type,
            timestamp=ts,
            payload=payload,
            context=context_store,
            correlation_id=correlation_id,
            parent_event_id=parent_event_id,
        )
        db.add(row)
        await db.flush()

        mesh_event = MeshEvent(
            event_id=event_id,
            tenant_id=tenant_id,
            device_id=device_id,
            domain=domain,
            event_type=event_type,
            timestamp=ts,
            payload=payload,
            context=resolved,
            correlation_id=correlation_id,
            parent_event_id=parent_event_id,
        )
        envelope = mesh_event.model_dump(mode="json")
        topic = mesh_event_topic(str(tenant_id), domain, event_type)
        await self._mqtt.publish_json(topic, envelope)
        await self._redis.publish(mesh_tenant_fanout_channel(str(tenant_id)), json.dumps(envelope, default=str))
        return event_id


def init_mesh_publisher(redis: RedisClient, mqtt: MqttPublisherProtocol) -> MeshEventPublisher:
    global _mesh_publisher
    _mesh_publisher = MeshEventPublisher(redis, mqtt)
    return _mesh_publisher


def get_mesh_publisher() -> MeshEventPublisher | None:
    return _mesh_publisher
