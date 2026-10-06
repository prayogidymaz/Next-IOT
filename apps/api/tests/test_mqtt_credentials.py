"""MQTT credentials, EMQX webhooks, ACL, and QR claim tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
import redis.asyncio as aioredis
from app.config import settings
from app.database import async_session
from app.device_profiles.spec import TelemetryKeyBoolean, ThingModelSpec
from app.models.device_credential import DeviceCredential, generate_access_token
from app.mqtt_auth.acl import MqttAclDecision, evaluate_device_acl, parse_device_topic
from app.mqtt_auth.cache import set_cached_credential
from httpx import AsyncClient
from sqlalchemy import select

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
        json={"name": "MqttDev", "device_type": "sensor"},
    )
    body = create.json()
    device_id = body["device"]["id"]
    gen = await client.post(
        f"/api/v1/devices/{device_id}/credentials",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert gen.status_code == 201
    data = gen.json()
    return device_id, data["access_token"], data["client_id"]


def test_device_credential_generate_unique_token() -> None:
    tokens = {generate_access_token() for _ in range(20)}
    assert len(tokens) == 20


@pytest.mark.asyncio
async def test_device_credential_rotate_invalidates_old(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    device_id, first_token, _ = await _device_with_credential(client, token)
    rotate = await client.post(
        f"/api/v1/devices/{device_id}/credentials/rotate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rotate.status_code == 200
    second = rotate.json()["access_token"]
    auth_old = await client.post(
        "/api/v1/mqtt/auth",
        headers=_webhook_headers(),
        json={"username": first_token, "clientid": "x"},
    )
    assert auth_old.json()["result"] == "deny"
    auth_new = await client.post(
        "/api/v1/mqtt/auth",
        headers=_webhook_headers(),
        json={"username": second, "clientid": "x"},
    )
    assert auth_new.json()["result"] == "allow"


@pytest.mark.asyncio
async def test_mqtt_auth_valid_token_returns_allow(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    _, access, _ = await _device_with_credential(client, token)
    resp = await client.post(
        "/api/v1/mqtt/auth",
        headers=_webhook_headers(),
        json={"username": access, "clientid": "dev"},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == "allow"


@pytest.mark.asyncio
async def test_mqtt_auth_invalid_token_returns_deny(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/mqtt/auth",
        headers=_webhook_headers(),
        json={"username": "invalid-token", "clientid": "dev"},
    )
    assert resp.json()["result"] == "deny"


@pytest.mark.asyncio
async def test_mqtt_auth_inactive_credential_returns_deny(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    device_id, access, _ = await _device_with_credential(client, token)
    revoke = await client.delete(
        f"/api/v1/devices/{device_id}/credentials",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert revoke.status_code == 204
    resp = await client.post(
        "/api/v1/mqtt/auth",
        headers=_webhook_headers(),
        json={"username": access, "clientid": "dev"},
    )
    assert resp.json()["result"] == "deny"


@pytest.mark.asyncio
async def test_mqtt_auth_updates_last_connected_at(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    device_id, access, _ = await _device_with_credential(client, token)
    await client.post(
        "/api/v1/mqtt/auth",
        headers=_webhook_headers(),
        json={"username": access, "clientid": "dev"},
    )
    async with async_session() as session:
        row = await session.scalar(select(DeviceCredential).where(DeviceCredential.access_token == access))
        assert row is not None
        assert row.last_connected_at is not None


@pytest.mark.asyncio
async def test_mqtt_auth_cache_hit_returns_fast(
    client: AsyncClient,
    test_redis: aioredis.Redis,
    unique_slug: str,
    unique_email: str,
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    device_id, access, _ = await _device_with_credential(client, token)
    tenant_id = uuid.UUID(
        (await client.get(f"/api/v1/devices/{device_id}", headers={"Authorization": f"Bearer {token}"})).json()[
            "tenant_id"
        ]
    )
    await set_cached_credential(
        test_redis,
        access,
        device_id=uuid.UUID(device_id),
        tenant_id=tenant_id,
    )
    resp = await client.post(
        "/api/v1/mqtt/auth",
        headers=_webhook_headers(),
        json={"username": access, "clientid": "dev"},
    )
    assert resp.json()["result"] == "allow"


def test_mqtt_acl_device_publish_own_topic_allow() -> None:
    tenant_id = uuid.uuid4()
    device_id = uuid.uuid4()
    topic = f"tenants/{tenant_id}/devices/{device_id}/telemetry"
    decision = evaluate_device_acl(
        credential_tenant_id=tenant_id,
        credential_device_id=device_id,
        topic=topic,
        action="publish",
    )
    assert decision == MqttAclDecision.ALLOW


def test_mqtt_acl_device_publish_other_topic_deny() -> None:
    tenant_id = uuid.uuid4()
    device_id = uuid.uuid4()
    other = uuid.uuid4()
    topic = f"tenants/{tenant_id}/devices/{other}/telemetry"
    decision = evaluate_device_acl(
        credential_tenant_id=tenant_id,
        credential_device_id=device_id,
        topic=topic,
        action="publish",
    )
    assert decision == MqttAclDecision.DENY


def test_mqtt_acl_device_publish_other_tenant_deny() -> None:
    tenant_id = uuid.uuid4()
    other_tenant = uuid.uuid4()
    device_id = uuid.uuid4()
    topic = f"tenants/{other_tenant}/devices/{device_id}/telemetry"
    decision = evaluate_device_acl(
        credential_tenant_id=tenant_id,
        credential_device_id=device_id,
        topic=topic,
        action="publish",
    )
    assert decision == MqttAclDecision.DENY


def test_mqtt_acl_device_subscribe_own_commands_allow() -> None:
    tenant_id = uuid.uuid4()
    device_id = uuid.uuid4()
    topic = f"tenants/{tenant_id}/devices/{device_id}/commands/turn_on"
    decision = evaluate_device_acl(
        credential_tenant_id=tenant_id,
        credential_device_id=device_id,
        topic=topic,
        action="subscribe",
    )
    assert decision == MqttAclDecision.ALLOW


def test_mqtt_acl_malformed_topic_deny() -> None:
    assert parse_device_topic("invalid/topic") is None


@pytest.mark.asyncio
async def test_mqtt_ingest_telemetry_webhook_validates_source(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/mqtt/ingest/telemetry",
        json={"topic": "tenants/x/devices/y/telemetry", "payload": "{}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_mqtt_ingest_telemetry_reuses_pipeline(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    device_id, access, _ = await _device_with_credential(client, token)
    device = await client.get(f"/api/v1/devices/{device_id}", headers={"Authorization": f"Bearer {token}"})
    tenant_id = device.json()["tenant_id"]
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
            "key": f"mq_{unique_slug.replace('-', '_')[:20]}",
            "name": "mq",
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
    bad = await client.post(
        "/api/v1/mqtt/ingest/telemetry",
        headers=_webhook_headers(),
        json={
            "topic": topic,
            "username": access,
            "payload": '{"ts":"2026-10-06T12:00:00Z","values":{"relay_on":"nope"}}',
        },
    )
    assert bad.json()["accepted_count"] == 0


@pytest.mark.asyncio
async def test_claim_token_generate_with_profile(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    resp = await client.post(
        "/api/v1/device-claim-tokens",
        headers={"Authorization": f"Bearer {token}"},
        json={"device_name": "Claimed", "device_type": "sensor", "device_category": "FIELD_SENSORS_LORA"},
    )
    assert resp.status_code == 201
    assert "nextiot://claim" in resp.json()["qr_code_url"]


@pytest.mark.asyncio
async def test_claim_token_expires_cannot_claim(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    created = await client.post(
        "/api/v1/device-claim-tokens",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "device_name": "Late",
            "device_type": "sensor",
            "device_category": "FIELD_SENSORS_LORA",
            "ttl_hours": 1,
        },
    )
    claim_token = created.json()["claim_token"]
    async with async_session() as session:
        from app.models.device_claim_token import DeviceClaimToken

        row = await session.scalar(select(DeviceClaimToken).where(DeviceClaimToken.claim_token == claim_token))
        assert row is not None
        row.expires_at = datetime.now(UTC) - timedelta(hours=1)
        await session.commit()
    claim = await client.post(f"/api/v1/device-claim-tokens/{claim_token}/claim")
    assert claim.status_code == 410


@pytest.mark.asyncio
async def test_claim_token_claim_creates_device_and_credential(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    created = await client.post(
        "/api/v1/device-claim-tokens",
        headers={"Authorization": f"Bearer {token}"},
        json={"device_name": "QR", "device_type": "sensor", "device_category": "FIELD_SENSORS_LORA"},
    )
    claim_token = created.json()["claim_token"]
    claim = await client.post(f"/api/v1/device-claim-tokens/{claim_token}/claim")
    assert claim.status_code == 200
    body = claim.json()
    assert body["access_token"]
    assert body["mqtt_broker_url"] == settings.mqtt_broker_url_external


@pytest.mark.asyncio
async def test_claim_token_claim_twice_fails(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    created = await client.post(
        "/api/v1/device-claim-tokens",
        headers={"Authorization": f"Bearer {token}"},
        json={"device_name": "Once", "device_type": "sensor", "device_category": "FIELD_SENSORS_LORA"},
    )
    claim_token = created.json()["claim_token"]
    first = await client.post(f"/api/v1/device-claim-tokens/{claim_token}/claim")
    assert first.status_code == 200
    second = await client.post(f"/api/v1/device-claim-tokens/{claim_token}/claim")
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_claim_token_wrong_tenant_denied(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token_a = await _register_token(client, unique_slug, unique_email)
    created = await client.post(
        "/api/v1/device-claim-tokens",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"device_name": "Iso", "device_type": "sensor", "device_category": "FIELD_SENSORS_LORA"},
    )
    token_id = created.json()["id"]
    slug_b = f"b-{uuid.uuid4().hex[:8]}"
    token_b = await _register_token(client, slug_b, f"{slug_b}@example.com")
    delete = await client.delete(
        f"/api/v1/device-claim-tokens/{token_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert delete.status_code == 404


@pytest.mark.asyncio
async def test_qr_claim_response_includes_mqtt_url(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _register_token(client, unique_slug, unique_email)
    created = await client.post(
        "/api/v1/device-claim-tokens",
        headers={"Authorization": f"Bearer {token}"},
        json={"device_name": "Url", "device_type": "sensor", "device_category": "FIELD_SENSORS_LORA"},
    )
    claim = await client.post(f"/api/v1/device-claim-tokens/{created.json()['claim_token']}/claim")
    assert claim.json()["mqtt_broker_url"].startswith("mqtt://")
