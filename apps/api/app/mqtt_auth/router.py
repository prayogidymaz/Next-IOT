from __future__ import annotations

import json
import logging
from typing import Annotated

from app.deps import DbSession, RedisDep
from app.mqtt_auth.deps import require_mqtt_webhook_secret
from app.mqtt_auth.ingest import ingest_mqtt_telemetry
from app.mqtt_auth.rate_limit import (
    enforce_mqtt_auth_rate_limit,
    enforce_mqtt_ingest_rate_limit,
    track_device_message_rates,
)
from app.mqtt_auth.schemas import (
    MqttAclRequest,
    MqttAclResponse,
    MqttAuthRequest,
    MqttAuthResponse,
    MqttTelemetryIngestRequest,
)
from app.mqtt_auth.service import handle_mqtt_acl, handle_mqtt_auth
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mqtt", tags=["mqtt"])

MqttWebhookAuth = Annotated[None, Depends(require_mqtt_webhook_secret)]


@router.post("/auth", response_model=MqttAuthResponse)
async def mqtt_auth(
    payload: MqttAuthRequest,
    db: DbSession,
    redis: RedisDep,
    request: Request,
    _: MqttWebhookAuth,
) -> MqttAuthResponse:
    await enforce_mqtt_auth_rate_limit(redis, request)
    return await handle_mqtt_auth(db, redis, payload)


@router.post("/acl", response_model=MqttAclResponse)
async def mqtt_acl(
    payload: MqttAclRequest,
    db: DbSession,
    redis: RedisDep,
    request: Request,
    _: MqttWebhookAuth,
) -> MqttAclResponse:
    await enforce_mqtt_auth_rate_limit(redis, request)
    return await handle_mqtt_acl(db, redis, payload)


@router.post("/ingest/telemetry")
async def mqtt_ingest_telemetry(
    request: Request,
    db: DbSession,
    redis: RedisDep,
    _: MqttWebhookAuth,
) -> dict[str, int | list[str]]:
    raw_body = await request.body()
    logger.info(
        "MQTT INGEST RAW BODY len=%d first500=%r",
        len(raw_body),
        raw_body[:500],
    )
    try:
        data_dict = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        logger.error("Raw body not valid JSON: %s | body=%r", exc, raw_body[:200])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON body: {exc}",
        ) from exc
    if not isinstance(data_dict, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body: root must be an object",
        )
    try:
        payload_model = MqttTelemetryIngestRequest.model_validate(data_dict)
    except ValidationError as exc:
        logger.error("Schema validation failed: %s | data_keys=%s", exc, list(data_dict.keys()))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ) from exc

    await enforce_mqtt_ingest_rate_limit(redis, request)
    result = await ingest_mqtt_telemetry(db, redis, payload_model)
    rejected = result.get("rejected")
    if isinstance(rejected, list) and payload_model.username:
        topic_parts = payload_model.topic.strip("/").split("/")
        if len(topic_parts) >= 4:
            await track_device_message_rates(
                redis,
                tenant_id=topic_parts[1],
                device_id=topic_parts[3],
            )
    return result
