"""Device attributes API and MQTT ingest."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.database import async_session
from app.main import app
from app.models.device_attribute import DeviceAttribute, DeviceAttributeScope
from app.mqtt_subscriber.service import MqttSubscriberService
from httpx import AsyncClient
from sqlalchemy import select
from tests.mqtt_subscriber.test_subscriber_service import _register_device_online

PASSWORD = "SecurePass123!"


async def _admin_token(client: AsyncClient, slug: str, email: str) -> str:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"T {slug}",
            "tenant_slug": slug,
            "email": email,
            "password": PASSWORD,
        },
    )
    assert reg.status_code == 201
    return reg.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_server_attribute_create_requires_operator(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _admin_token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "AttrOp", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    viewer_email = f"viewer-{uuid.uuid4().hex[:6]}@example.com"
    from app.auth.security import hash_password
    from app.database import async_session as session_factory
    from app.models.tenant_membership import TenantMembership
    from app.models.user import User

    tenant_id = uuid.UUID(create.json()["device"]["tenant_id"])
    async with session_factory() as db:
        viewer = User(
            tenant_id=tenant_id,
            email=viewer_email,
            password_hash=hash_password(PASSWORD),
            role="viewer",
        )
        db.add(viewer)
        await db.flush()
        db.add(TenantMembership(user_id=viewer.id, tenant_id=tenant_id, role="viewer"))
        await db.commit()
    viewer_token = (
        await client.post("/auth/login", json={"email": viewer_email, "password": PASSWORD})
    ).json()["access_token"]
    denied = await client.put(
        f"/api/v1/devices/{device_id}/attributes/server/location",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={"value": "A1"},
    )
    assert denied.status_code == 403
    allowed = await client.put(
        f"/api/v1/devices/{device_id}/attributes/server/location",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": "Warehouse A1"},
    )
    assert allowed.status_code == 200


@pytest.mark.asyncio
async def test_shared_attribute_create_broadcasts_mqtt(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _admin_token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "AttrShared", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    mock_pub = AsyncMock()
    app.state.mqtt_publisher = mock_pub
    resp = await client.put(
        f"/api/v1/devices/{device_id}/attributes/shared/sampling_rate_s",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": 60},
    )
    assert resp.status_code == 200
    mock_pub.publish_json.assert_awaited_once()


@pytest.mark.asyncio
async def test_client_attribute_api_create_rejected_400(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _admin_token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "AttrClient", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    resp = await client.put(
        f"/api/v1/devices/{device_id}/attributes/client/firmware_version",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": "1.0.0"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_client_attribute_via_mqtt_subscriber_persisted(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    device_id, tenant_id = await _register_device_online(
        client, unique_slug, unique_email, name="AttrMqtt"
    )
    message = MagicMock()
    message.topic = f"tenants/{tenant_id}/devices/{device_id}/attributes"
    message.payload = b'{"firmware_version":"1.2.3","uptime_seconds":3600}'
    service = MqttSubscriberService(test_redis)
    await service._handle_client_attributes(message, message.topic)
    async with async_session() as verify:
        row = await verify.scalar(
            select(DeviceAttribute).where(
                DeviceAttribute.device_id == uuid.UUID(device_id),
                DeviceAttribute.scope == DeviceAttributeScope.CLIENT,
                DeviceAttribute.key == "firmware_version",
            )
        )
    assert row is not None
    assert row.value_json == "1.2.3"


@pytest.mark.asyncio
async def test_attribute_delete_removes_row(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _admin_token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "AttrDel", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    await client.put(
        f"/api/v1/devices/{device_id}/attributes/server/tag",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": "x"},
    )
    deleted = await client.delete(
        f"/api/v1/devices/{device_id}/attributes/server/tag",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deleted.status_code == 204
    missing = await client.get(
        f"/api/v1/devices/{device_id}/attributes/server/tag",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_attribute_list_by_scope(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _admin_token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "AttrList", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    await client.put(
        f"/api/v1/devices/{device_id}/attributes/server/a_key",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": 1},
    )
    await client.put(
        f"/api/v1/devices/{device_id}/attributes/shared/b_key",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": 2},
    )
    listed = await client.get(
        f"/api/v1/devices/{device_id}/attributes",
        headers={"Authorization": f"Bearer {token}"},
        params={"scope": "server"},
    )
    assert listed.status_code == 200
    keys = {item["key"] for item in listed.json()["items"]}
    assert keys == {"a_key"}


@pytest.mark.asyncio
async def test_attribute_key_pattern_validation(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _admin_token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "AttrKey", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    bad = await client.put(
        f"/api/v1/devices/{device_id}/attributes/server/Bad-Key",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": 1},
    )
    assert bad.status_code == 422


@pytest.mark.asyncio
async def test_attribute_value_json_any_type(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token = await _admin_token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "AttrTypes", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    cases = [
        ("str_val", "hello"),
        ("num_val", 42),
        ("bool_val", True),
        ("obj_val", {"nested": [1, 2]}),
        ("arr_val", [1, "two", False]),
    ]
    for key, value in cases:
        resp = await client.put(
            f"/api/v1/devices/{device_id}/attributes/server/{key}",
            headers={"Authorization": f"Bearer {token}"},
            json={"value": value},
        )
        assert resp.status_code == 200
        assert resp.json()["value"] == value


@pytest.mark.asyncio
async def test_attribute_tenant_isolation(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token_a = await _admin_token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"name": "Iso", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    slug_b = f"tenant-{uuid.uuid4().hex[:8]}"
    token_b = await _admin_token(client, slug_b, f"b-{uuid.uuid4().hex[:8]}@example.com")
    foreign = await client.get(
        f"/api/v1/devices/{device_id}/attributes",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert foreign.status_code == 404


@pytest.mark.asyncio
async def test_mqtt_subscriber_commits_client_attributes(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    device_id, tenant_id = await _register_device_online(
        client, unique_slug, unique_email, name="AttrCommit"
    )
    message = MagicMock()
    message.topic = f"tenants/{tenant_id}/devices/{device_id}/attributes"
    message.payload = b'{"ip_address":"10.0.0.5"}'
    await MqttSubscriberService(test_redis)._handle(message)
    async with async_session() as verify:
        row = await verify.scalar(
            select(DeviceAttribute).where(
                DeviceAttribute.device_id == uuid.UUID(device_id),
                DeviceAttribute.key == "ip_address",
            )
        )
    assert row is not None
