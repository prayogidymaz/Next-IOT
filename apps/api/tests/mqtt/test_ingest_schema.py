"""EMQX whole-event ingest body and flexible payload typing."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from app.config import settings
from app.mqtt_auth.payload_parse import telemetry_payload_object
from app.mqtt_auth.schemas import MqttTelemetryIngestRequest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


def _webhook_headers() -> dict[str, str]:
    return {"X-Internal-Secret": settings.mqtt_webhook_shared_secret}


async def _register_token(client: AsyncClient, slug: str, email: str) -> str:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    assert reg.status_code == 201
    return reg.json()["tokens"]["access_token"]


async def _device_with_credential(client: AsyncClient, token: str) -> tuple[str, str, str]:
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "SchemaDev", "device_type": "sensor"},
    )
    body = create.json()
    device_id = body["device"]["id"]
    tenant_id = body["device"]["tenant_id"]
    gen = await client.post(
        f"/api/v1/devices/{device_id}/credentials",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert gen.status_code == 201
    return tenant_id, device_id, gen.json()["access_token"]


def test_telemetry_payload_object_decodes_bytes_utf8() -> None:
    body = MqttTelemetryIngestRequest(
        topic="tenants/t/d/telemetry",
        payload=b'{"values":{"temp":1}}',
    )
    parsed = telemetry_payload_object(body)
    assert parsed["values"] == {"temp": 1}


@pytest.mark.asyncio
async def test_ingest_accepts_whole_emqx_event(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    tenant_id, device_id, access = await _device_with_credential(client, token)
    topic = f"tenants/{tenant_id}/devices/{device_id}/telemetry"
    with patch(
        "app.mqtt_auth.ingest.persist_telemetry_from_mqtt",
        new_callable=AsyncMock,
        return_value={"accepted_count": 1, "rejected": []},
    ) as mock_ingest:
        resp = await client.post(
            "/api/v1/mqtt/ingest/telemetry",
            headers=_webhook_headers(),
            json={
                "topic": topic,
                "username": access,
                "clientid": "dev_testclient",
                "payload": {"ts": "2026-10-09T12:00:00Z", "values": {"temperature": 42}},
                "qos": 1,
                "retain": False,
                "peerhost": "172.21.0.1",
                "event": "message.publish",
                "metadata": {"rule_id": "rule_forward_telemetry"},
                "pub_props": {},
                "timestamp": 1_728_000_000_000,
                "node": "emqx@127.0.0.1",
                "id": "00000000-0000-0000-0000-000000000001",
            },
        )
    assert resp.status_code == 200
    mock_ingest.assert_awaited_once()


@pytest.mark.asyncio
async def test_ingest_payload_as_json_string_parses_correctly(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    tenant_id, device_id, access = await _device_with_credential(client, token)
    topic = f"tenants/{tenant_id}/devices/{device_id}/telemetry"
    with patch(
        "app.mqtt_auth.ingest.persist_telemetry_from_mqtt",
        new_callable=AsyncMock,
        return_value={"accepted_count": 1, "rejected": []},
    ) as mock_ingest:
        resp = await client.post(
            "/api/v1/mqtt/ingest/telemetry",
            headers=_webhook_headers(),
            json={
                "topic": topic,
                "username": access,
                "payload": '{"ts":"2026-10-09T12:00:00Z","values":{"humidity":55}}',
            },
        )
    assert resp.status_code == 200
    mock_ingest.assert_awaited_once()


@pytest.mark.asyncio
async def test_ingest_payload_as_dict_pass_through(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    tenant_id, device_id, access = await _device_with_credential(client, token)
    topic = f"tenants/{tenant_id}/devices/{device_id}/telemetry"
    with patch(
        "app.mqtt_auth.ingest.persist_telemetry_from_mqtt",
        new_callable=AsyncMock,
        return_value={"accepted_count": 1, "rejected": []},
    ) as mock_ingest:
        resp = await client.post(
            "/api/v1/mqtt/ingest/telemetry",
            headers=_webhook_headers(),
            json={
                "topic": topic,
                "username": access,
                "payload": {"values": {"pressure": 1013}},
            },
        )
    assert resp.status_code == 200
    mock_ingest.assert_awaited_once()
