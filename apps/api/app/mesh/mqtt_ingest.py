"""Ingest mesh events published over MQTT (device simulators)."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mesh.event_bus import MeshDomain, mesh_tenant_fanout_channel
from app.mesh.schemas import MeshContext, MeshEvent
from app.models.mesh_event import MeshEventRecord
from app.types.json_types import JsonObject, JsonValue
from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)


def parse_mesh_mqtt_topic(topic: str) -> tuple[uuid.UUID, str, str] | None:
    parts = topic.split("/")
    if len(parts) < 6:
        return None
    if parts[0] != "tenants" or parts[2] != "mesh" or parts[3] != "events":
        return None
    try:
        tenant_id = uuid.UUID(parts[1])
    except ValueError:
        return None
    domain = parts[4]
    event_type = parts[5]
    return tenant_id, domain, event_type


def _context_from_raw(raw: object) -> MeshContext:
    if not isinstance(raw, dict):
        return MeshContext()
    return MeshContext.model_validate(raw)


async def ingest_mesh_event_from_mqtt(
    db: AsyncSession,
    redis: RedisClient,
    *,
    topic: str,
    payload_obj: dict[str, JsonValue],
) -> bool:
    parsed = parse_mesh_mqtt_topic(topic)
    if parsed is None:
        return False
    tenant_id, domain_str, event_type = parsed
    try:
        domain = MeshDomain(domain_str)
    except ValueError:
        logger.warning("Mesh MQTT ingest ignored unknown domain topic=%s", topic)
        return False

    event_id_raw = payload_obj.get("event_id")
    device_raw = payload_obj.get("device_id")
    if event_id_raw is None or device_raw is None:
        return False
    try:
        event_id = uuid.UUID(str(event_id_raw))
        device_id = uuid.UUID(str(device_raw))
    except ValueError:
        return False

    ts_raw = payload_obj.get("timestamp")
    if isinstance(ts_raw, str):
        timestamp = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
    elif isinstance(ts_raw, datetime):
        timestamp = ts_raw
    else:
        timestamp = datetime.now(tz=UTC)

    payload_raw = payload_obj.get("payload")
    payload: JsonObject = payload_raw if isinstance(payload_raw, dict) else {}
    context = _context_from_raw(payload_obj.get("context"))

    correlation_raw = payload_obj.get("correlation_id")
    parent_raw = payload_obj.get("parent_event_id")
    correlation_id = uuid.UUID(str(correlation_raw)) if correlation_raw else None
    parent_event_id = uuid.UUID(str(parent_raw)) if parent_raw else None

    existing = await db.scalar(select(MeshEventRecord.id).where(MeshEventRecord.id == event_id))
    if existing is None:
        row = MeshEventRecord(
            id=event_id,
            tenant_id=tenant_id,
            device_id=device_id,
            domain=domain.value,
            event_type=event_type,
            timestamp=timestamp,
            payload=payload,
            context=context.model_dump(mode="json"),
            correlation_id=correlation_id,
            parent_event_id=parent_event_id,
        )
        db.add(row)
        await db.flush()

    envelope = MeshEvent(
        event_id=event_id,
        tenant_id=tenant_id,
        device_id=device_id,
        domain=domain,
        event_type=event_type,
        timestamp=timestamp,
        payload=payload,
        context=context,
        correlation_id=correlation_id,
        parent_event_id=parent_event_id,
    ).model_dump(mode="json")
    await redis.publish(mesh_tenant_fanout_channel(str(tenant_id)), json.dumps(envelope, default=str))
    return True
