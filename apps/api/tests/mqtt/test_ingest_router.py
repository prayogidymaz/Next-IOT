"""MQTT ingest endpoint raw body logging and parse errors."""

from __future__ import annotations

import logging
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.config import settings

PASSWORD = "SecurePass123!"


def _webhook_headers() -> dict[str, str]:
    return {"X-Internal-Secret": settings.mqtt_webhook_shared_secret}


@pytest.mark.asyncio
async def test_ingest_endpoint_logs_raw_body(client: AsyncClient) -> None:
    raw = b'{"topic":"tenants/x/devices/y/telemetry","payload":"{}"}'
    with patch.object(logging.getLogger("app.mqtt_auth.router"), "info") as log_info:
        await client.post(
            "/api/v1/mqtt/ingest/telemetry",
            headers={**_webhook_headers(), "Content-Type": "application/json"},
            content=raw,
        )
    assert log_info.call_count >= 1
    first_message = log_info.call_args_list[0][0][0]
    assert first_message == "MQTT INGEST RAW BODY len=%d first500=%r"
    assert log_info.call_args_list[0][0][1] == len(raw)
    assert log_info.call_args_list[0][0][2] == raw[:500]


@pytest.mark.asyncio
async def test_ingest_endpoint_rejects_invalid_json_with_400(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/mqtt/ingest/telemetry",
        headers={**_webhook_headers(), "Content-Type": "application/json"},
        content=b"not-valid-json",
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert isinstance(detail, str)
    assert detail.startswith("Invalid JSON body:")


@pytest.mark.asyncio
async def test_ingest_endpoint_rejects_valid_json_wrong_schema_with_422(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/mqtt/ingest/telemetry",
        headers=_webhook_headers(),
        json={"username": "token-only-no-topic", "payload": {}},
    )
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert isinstance(detail, list)
    assert len(detail) >= 1
