"""MQTT telemetry ingest via EMQX HTTP rule (reuses ingest_pipeline)."""

from __future__ import annotations

from app.device_credentials.service import lookup_active_by_access_token
from app.mqtt_auth.acl import parse_device_topic
from app.mqtt_auth.payload_parse import telemetry_payload_object
from app.mqtt_auth.schemas import MqttTelemetryIngestRequest
from app.mqtt_subscriber.schemas import TelemetryMqttTopic
from app.mqtt_subscriber.telemetry_ingest import persist_telemetry_from_mqtt
from app.types.redis_client import RedisClient
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


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
    topic_model = TelemetryMqttTopic.from_mqtt_topic(body.topic)
    return await persist_telemetry_from_mqtt(
        db,
        redis,
        topic=topic_model,
        payload_obj=payload_obj,
        client_id=body.clientid or "mqtt-ingest",
    )
