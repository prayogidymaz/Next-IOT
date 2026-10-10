"""MQTT ingest endpoint raw body logging and parse errors."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from app.config import settings
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


def _webhook_headers() -> dict[str, str]:
    return {"X-Internal-Secret": settings.mqtt_webhook_shared_secret}


@pytest.mark.asyncio
async def test_ingest_endpoint_logs_raw_body(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Raw-body parser returns structured 400; optional debug log when MQTT_DEBUG_RAW_BODY=true."""
    from app.config import settings

    monkeypatch.setattr(settings, "mqtt_debug_raw_body", True)
    with patch("app.mqtt_auth.router.logger") as log:
        resp = await client.post(
            "/api/v1/mqtt/ingest/telemetry",
            headers={**_webhook_headers(), "Content-Type": "application/json"},
            content=b"{not-closed",
        )
    assert resp.status_code == 400
    assert log.warning.call_count >= 1
    detail = resp.json()["detail"]
    assert isinstance(detail, str)
    assert detail.startswith("Invalid JSON body:")


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
