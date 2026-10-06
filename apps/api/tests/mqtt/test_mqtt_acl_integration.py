"""Integration tests for EMQX ACL webhook endpoint (/api/v1/mqtt/acl)."""

from __future__ import annotations

import uuid

import pytest
from app.config import settings
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


async def _device_access_token(client: AsyncClient, user_token: str) -> tuple[str, str, str]:
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "AclDev", "device_type": "sensor"},
    )
    assert create.status_code == 201
    device_id = create.json()["device"]["id"]
    tenant_id = create.json()["device"]["tenant_id"]
    gen = await client.post(
        f"/api/v1/devices/{device_id}/credentials",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert gen.status_code == 201
    access_token = gen.json()["access_token"]
    return tenant_id, device_id, access_token


@pytest.mark.asyncio
async def test_acl_publish_own_topic_returns_allow(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    user_token = await _register_token(client, unique_slug, unique_email)
    tenant_id, device_id, access_token = await _device_access_token(client, user_token)
    topic = f"tenants/{tenant_id}/devices/{device_id}/telemetry"
    resp = await client.post(
        "/api/v1/mqtt/acl",
        headers=_webhook_headers(),
        json={"username": access_token, "clientid": "dev", "topic": topic, "action": "publish"},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == "allow"


@pytest.mark.asyncio
async def test_acl_publish_other_device_topic_returns_deny(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    user_token = await _register_token(client, unique_slug, unique_email)
    tenant_id, device_id, access_token = await _device_access_token(client, user_token)
    other_device = uuid.uuid4()
    topic = f"tenants/{tenant_id}/devices/{other_device}/telemetry"
    resp = await client.post(
        "/api/v1/mqtt/acl",
        headers=_webhook_headers(),
        json={"username": access_token, "clientid": "dev", "topic": topic, "action": "publish"},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == "deny"


@pytest.mark.asyncio
async def test_acl_publish_other_tenant_topic_returns_deny(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    user_token = await _register_token(client, unique_slug, unique_email)
    tenant_id, device_id, access_token = await _device_access_token(client, user_token)
    other_tenant = uuid.uuid4()
    topic = f"tenants/{other_tenant}/devices/{device_id}/telemetry"
    resp = await client.post(
        "/api/v1/mqtt/acl",
        headers=_webhook_headers(),
        json={"username": access_token, "clientid": "dev", "topic": topic, "action": "publish"},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == "deny"


@pytest.mark.asyncio
async def test_acl_malformed_topic_returns_deny(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    user_token = await _register_token(client, unique_slug, unique_email)
    _, _, access_token = await _device_access_token(client, user_token)
    resp = await client.post(
        "/api/v1/mqtt/acl",
        headers=_webhook_headers(),
        json={"username": access_token, "clientid": "dev", "topic": "invalid/topic", "action": "publish"},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == "deny"


@pytest.mark.asyncio
async def test_acl_webhook_rejects_missing_secret_header(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    user_token = await _register_token(client, unique_slug, unique_email)
    tenant_id, device_id, access_token = await _device_access_token(client, user_token)
    topic = f"tenants/{tenant_id}/devices/{device_id}/telemetry"
    resp = await client.post(
        "/api/v1/mqtt/acl",
        json={"username": access_token, "clientid": "dev", "topic": topic, "action": "publish"},
    )
    assert resp.status_code == 403
