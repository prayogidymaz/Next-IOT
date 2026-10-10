"""MQTT telemetry ingest via EMQX HTTP rule (reuses ingest_pipeline)."""

from __future__ import annotations

from datetime import UTC, datetime

from app.device_credentials.service import lookup_active_by_access_token
from app.devices.dependencies import CurrentDevice
from app.models.device import Device
from app.mqtt_auth.acl import parse_device_topic
from app.mqtt_auth.payload_parse import telemetry_payload_object
from app.mqtt_auth.schemas import MqttTelemetryIngestRequest
from app.telemetry.ingest_pipeline import split_telemetry_for_profile
from app.telemetry.profile_loader import load_thing_model_for_device
from app.telemetry.schemas import TelemetryIngestRequest
from app.telemetry.service import ingest_telemetry
from app.types.redis_client import RedisClient
from fastapi import HTTPException, status
from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def _parse_timestamp(raw: str | None) -> datetime:
    if raw is None or not raw.strip():
        return datetime.now(UTC)
    normalized = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


async def ingest_mqtt_telemetry(
    db: AsyncSession,
    redis: RedisClient,
    body: MqttTelemetryIngestRequest,
) -> dict[str, int | list[str]]:
    parsed_topic = parse_device_topic(body.topic)
    if parsed_topic is None or parsed_topic.suffix != "telemetry":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid telemetry topic")

    access_token = body.username.strip() or body.clientid.strip()
    if not access_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing credential token")
    credential = await lookup_active_by_access_token(db, access_token)
    if credential is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credential token")
    if (
        credential.device_id != parsed_topic.device_id
        or credential.tenant_id != parsed_topic.tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Credential does not match topic device",
        )

    payload_obj = telemetry_payload_object(body)

    values_raw = payload_obj.get("values")
    if not isinstance(values_raw, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing values object")
    metrics: dict[str, JsonValue] = {}
    for key, value in values_raw.items():
        if isinstance(key, str):
            metrics[key] = value

    ts_raw = payload_obj.get("ts")
    recorded_at = _parse_timestamp(ts_raw if isinstance(ts_raw, str) else None)

    device = await db.scalar(
        select(Device).where(
            Device.id == parsed_topic.device_id,
            Device.tenant_id == parsed_topic.tenant_id,
        )
    )
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    spec = await load_thing_model_for_device(db, device)
    split = split_telemetry_for_profile(spec, metrics)
    if not split.metrics_to_persist:
        return {"accepted_count": 0, "rejected": [entry.key for entry in split.rejected]}

    current = CurrentDevice(
        device_id=device.id,
        tenant_id=device.tenant_id,
        client_id=body.clientid or "mqtt-ingest",
        status=device.status,
    )
    ingest_req = TelemetryIngestRequest(timestamp=recorded_at, metrics=split.metrics_to_persist)
    await ingest_telemetry(db, redis, current, ingest_req)
    return {"accepted_count": 1, "rejected": [entry.key for entry in split.rejected]}
