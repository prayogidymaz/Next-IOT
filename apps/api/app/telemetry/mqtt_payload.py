"""Shared MQTT telemetry JSON payload parsing."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from fastapi import HTTPException, status
from pydantic import JsonValue


def _parse_timestamp(raw: str | None) -> datetime:
    if raw is None or not raw.strip():
        return datetime.now(UTC)
    normalized = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def parse_telemetry_payload_bytes(payload: bytes) -> dict[str, JsonValue]:
    if not payload:
        return {}
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload is not valid UTF-8",
        ) from exc
    if not text.strip():
        return {}
    try:
        parsed = json.loads(text)
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


def parse_telemetry_payload_object(payload_obj: dict[str, JsonValue]) -> tuple[dict[str, JsonValue], datetime]:
    values_raw = payload_obj.get("values")
    if not isinstance(values_raw, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing values object")
    metrics: dict[str, JsonValue] = {}
    for key, value in values_raw.items():
        if isinstance(key, str):
            metrics[key] = value
    ts_raw = payload_obj.get("ts")
    recorded_at = _parse_timestamp(ts_raw if isinstance(ts_raw, str) else None)
    return metrics, recorded_at
