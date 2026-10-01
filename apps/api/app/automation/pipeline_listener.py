"""Background Redis pub/sub listener for automation pipeline events."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid

import redis.asyncio as aioredis

from app.automation.events import AUTOMATION_EVENTS_CHANNEL
from app.automation.pipeline_interpreter import pipeline_interpreter_service
from app.database import async_session
from app.mission.sar_emergency_events import SAR_EMERGENCY_CHANNEL

logger = logging.getLogger(__name__)


def _resolve_event(payload: dict) -> tuple[str | None, dict]:
    if payload.get("event_type"):
        return str(payload["event_type"]), payload.get("context") or {}

    incident = payload.get("incident") or {}
    event = str(payload.get("event", ""))
    if "ai" in event:
        metadata = incident.get("metadata") or {}
        return "AI_DETECTION", {
            "detection_class": metadata.get("detection_class", "person"),
            "confidence": metadata.get("confidence", 0.9),
            "lat": incident.get("target_lat"),
            "lon": incident.get("target_lon"),
            "device_id": incident.get("assigned_device_id"),
        }
    if incident.get("incident_type") == "DRONE_DOWN":
        return "TELEMETRY_ANOMALY", {
            "anomaly_type": "speed_deviation",
            "severity": "critical",
            "device_id": incident.get("assigned_device_id"),
            "lat": incident.get("target_lat"),
            "lon": incident.get("target_lon"),
        }
    if incident:
        return "GEOFENCE_BREACH", {
            "anomaly_type": "geofence_breach",
            "lat": incident.get("target_lat"),
            "lon": incident.get("target_lon"),
            "device_id": incident.get("assigned_device_id"),
        }
    return None, {}


async def _process_payload(redis: aioredis.Redis, payload: dict) -> None:
    tenant_raw = payload.get("tenant_id")
    if not tenant_raw:
        return

    event_type, context = _resolve_event(payload)
    if not event_type:
        return

    try:
        tenant_id = uuid.UUID(str(tenant_raw))
    except ValueError:
        return

    async with async_session() as db:
        try:
            await pipeline_interpreter_service.process_event(
                db,
                redis,
                tenant_id=tenant_id,
                event_type=event_type,
                context=context,
            )
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Automation pipeline event processing failed")


async def pipeline_listener_loop(redis: aioredis.Redis, stop_event: asyncio.Event) -> None:
    pubsub = redis.pubsub()
    await pubsub.subscribe(AUTOMATION_EVENTS_CHANNEL)
    await pubsub.psubscribe(f"{SAR_EMERGENCY_CHANNEL}*")
    logger.info("Automation pipeline listener started")

    while not stop_event.is_set():
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
        if message and message.get("type") in {"message", "pmessage"}:
            data = message.get("data")
            if isinstance(data, bytes):
                data = data.decode()
            if isinstance(data, str):
                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    payload = None
                if payload:
                    await _process_payload(redis, payload)
        await asyncio.sleep(0.05)

    await pubsub.unsubscribe(AUTOMATION_EVENTS_CHANNEL)
    await pubsub.punsubscribe(f"{SAR_EMERGENCY_CHANNEL}*")
    await pubsub.aclose()
    logger.info("Automation pipeline listener stopped")
