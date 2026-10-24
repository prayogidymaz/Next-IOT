"""Fire-and-forget mesh hooks for legacy pipelines."""

from __future__ import annotations

import asyncio
import logging
import uuid

from app.database import async_session
from app.mesh.event_bus import MeshDomain
from app.mesh.publisher import get_mesh_publisher
from app.types.json_types import JsonObject

logger = logging.getLogger(__name__)

_HIGH_ALARM_SEVERITIES = frozenset({"critical", "major"})


def schedule_sensor_reading_mesh_event(
    tenant_id: uuid.UUID,
    device_id: uuid.UUID,
    metrics: JsonObject,
    recorded_at_iso: str,
) -> None:
    async def _run() -> None:
        publisher = get_mesh_publisher()
        if publisher is None:
            return
        try:
            async with async_session() as db:
                await publisher.publish_event(
                    db,
                    tenant_id=tenant_id,
                    domain=MeshDomain.SENSOR,
                    event_type="reading_update",
                    device_id=device_id,
                    payload={"metrics": metrics, "recorded_at": recorded_at_iso},
                )
                await db.commit()
        except Exception:
            logger.exception("Mesh sensor reading publish failed device_id=%s", device_id)

    asyncio.create_task(_run())


def schedule_security_intrusion_mesh_event(
    tenant_id: uuid.UUID,
    device_id: uuid.UUID | None,
    alarm_id: uuid.UUID,
    severity: str,
    title: str,
) -> None:
    if severity.lower() not in _HIGH_ALARM_SEVERITIES:
        return
    if device_id is None:
        return

    async def _run() -> None:
        publisher = get_mesh_publisher()
        if publisher is None:
            return
        try:
            async with async_session() as db:
                await publisher.publish_event(
                    db,
                    tenant_id=tenant_id,
                    domain=MeshDomain.SECURITY,
                    event_type="intrusion_detected",
                    device_id=device_id,
                    payload={"alarm_id": str(alarm_id), "severity": severity, "title": title},
                )
                await db.commit()
        except Exception:
            logger.exception("Mesh security event publish failed alarm_id=%s", alarm_id)

    asyncio.create_task(_run())
