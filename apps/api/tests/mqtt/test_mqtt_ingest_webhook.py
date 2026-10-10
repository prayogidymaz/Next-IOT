"""MQTT telemetry ingest webhook tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from app.config import settings
from app.device_profiles.spec import TelemetryKeyBoolean, ThingModelSpec
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


def _webhook_headers(secret: str | None = None) -> dict[str, str]:
    value = secret if secret is not None else settings.mqtt_webhook_shared_secret
    return {"X-Internal-Secret": value}


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
        json={"name": "IngestDev", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    gen = await client.post(
        f"/api/v1/devices/{device_id}/credentials",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert gen.status_code == 201
    access = gen.json()["access_token"]
    tenant_id = create.json()["device"]["tenant_id"]
    return str(tenant_id), device_id, access


@pytest.mark.asyncio
async def test_ingest_webhook_rejects_missing_secret(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/mqtt/ingest/telemetry",
        json={"topic": "tenants/x/devices/y/telemetry", "payload": "{}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_ingest_webhook_rejects_wrong_secret(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/mqtt/ingest/telemetry",
        headers=_webhook_headers("wrong-secret"),
        json={"topic": "tenants/x/devices/y/telemetry", "payload": "{}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_ingest_webhook_parses_topic_correctly(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    _, device_id, access = await _device_with_credential(client, token)
    resp = await client.post(
        "/api/v1/mqtt/ingest/telemetry",
        headers=_webhook_headers(),
        json={"topic": "invalid/topic", "username": access, "payload": '{"values":{"t":1}}'},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_ingest_webhook_validates_credential_matches_topic(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    tenant_id, device_id, access = await _device_with_credential(client, token)
    other = uuid.uuid4()
    topic = f"tenants/{tenant_id}/devices/{other}/telemetry"
    resp = await client.post(
        "/api/v1/mqtt/ingest/telemetry",
        headers=_webhook_headers(),
        json={
            "topic": topic,
            "username": access,
            "payload": '{"values":{"temp":25}}',
        },
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_ingest_webhook_rejects_token_device_mismatch(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    tenant_id, _, access_a = await _device_with_credential(client, token)
    other_device = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Other", "device_type": "sensor"},
    )
    device_b = other_device.json()["device"]["id"]
    topic = f"tenants/{tenant_id}/devices/{device_b}/telemetry"
    resp = await client.post(
        "/api/v1/mqtt/ingest/telemetry",
        headers=_webhook_headers(),
        json={"topic": topic, "username": access_a, "payload": '{"values":{"temp":1}}'},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_ingest_webhook_calls_ingest_pipeline(
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
                "payload": '{"values":{"temp":25}}',
            },
        )
    assert resp.status_code == 200
    mock_ingest.assert_awaited_once()


@pytest.mark.asyncio
async def test_ingest_webhook_returns_partial_success(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    tenant_id, device_id, access = await _device_with_credential(client, token)
    await client.patch(
        f"/api/v1/devices/{device_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "online"},
    )
    spec = ThingModelSpec(
        telemetry=[TelemetryKeyBoolean(key="relay_on", label="Relay", data_type="boolean")],
        attributes=[],
        commands=[],
    )
    profile = await client.post(
        "/api/v1/device-profiles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "key": f"ing_{unique_slug.replace('-', '_')[:18]}",
            "name": "ing",
            "description": "",
            "domain": "generic",
            "spec": spec.model_dump(mode="json"),
        },
    )
    profile_id = profile.json()["id"]
    await client.post(f"/api/v1/device-profiles/{profile_id}/publish", headers={"Authorization": f"Bearer {token}"})
    await client.patch(
        f"/api/v1/devices/{device_id}/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"profile_id": profile_id},
    )
    topic = f"tenants/{tenant_id}/devices/{device_id}/telemetry"
    resp = await client.post(
        "/api/v1/mqtt/ingest/telemetry",
        headers=_webhook_headers(),
        json={
            "topic": topic,
            "username": access,
            "payload": '{"values":{"relay_on":"not-bool"}}',
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["accepted_count"] == 0
    rejected = body.get("rejected")
    assert isinstance(rejected, list)
