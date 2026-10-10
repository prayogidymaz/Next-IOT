"""Parse telemetry payload from EMQX ingest bodies."""

from __future__ import annotations

import json

from app.mqtt_auth.schemas import MqttTelemetryIngestRequest
from fastapi import HTTPException, status
from pydantic import JsonValue


def telemetry_payload_object(body: MqttTelemetryIngestRequest) -> dict[str, JsonValue]:
    raw = body.payload
    if isinstance(raw, str):
        if not raw.strip():
            return {}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload",
            ) from exc
        if not isinstance(parsed, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payload must be a JSON object",
            )
        return parsed
    if isinstance(raw, dict):
        return raw
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload type")
