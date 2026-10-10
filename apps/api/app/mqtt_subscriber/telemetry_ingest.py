"""Persist telemetry from raw MQTT publish (no device credential check)."""

from __future__ import annotations

from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.devices.dependencies import CurrentDevice
from app.models.device import Device
from app.mqtt_subscriber.schemas import TelemetryMqttTopic
from app.telemetry.ingest_pipeline import split_telemetry_for_profile
from app.telemetry.mqtt_payload import parse_telemetry_payload_object
from app.telemetry.profile_loader import load_thing_model_for_device
from app.telemetry.schemas import TelemetryIngestRequest
from app.telemetry.service import ingest_telemetry
from app.types.redis_client import RedisClient


async def persist_telemetry_from_mqtt(
    db: AsyncSession,
    redis: RedisClient,
    *,
    topic: TelemetryMqttTopic,
    payload_obj: dict[str, JsonValue],
    client_id: str,
) -> dict[str, int | list[str]]:
    metrics, recorded_at = parse_telemetry_payload_object(payload_obj)

    device = await db.scalar(
        select(Device).where(
            Device.id == topic.device_id,
            Device.tenant_id == topic.tenant_id,
        )
    )
    if device is None:
        return {"accepted_count": 0, "rejected": ["device_not_found"]}

    spec = await load_thing_model_for_device(db, device)
    split = split_telemetry_for_profile(spec, metrics)
    if not split.metrics_to_persist:
        return {"accepted_count": 0, "rejected": [entry.key for entry in split.rejected]}

    current = CurrentDevice(
        device_id=device.id,
        tenant_id=device.tenant_id,
        client_id=client_id,
        status=device.status,
    )
    ingest_req = TelemetryIngestRequest(timestamp=recorded_at, metrics=split.metrics_to_persist)
    await ingest_telemetry(db, redis, current, ingest_req)
    return {"accepted_count": 1, "rejected": [entry.key for entry in split.rejected]}
