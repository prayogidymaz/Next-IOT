"""Device RPC API and subscriber response handling."""

from __future__ import annotations

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.database import async_session
from app.main import app
from app.models.device_rpc_request import DeviceRpcRequest, DeviceRpcStatus
from app.mqtt_subscriber.service import MqttSubscriberService
from app.rpc.event_registry import RpcWaitResult, rpc_event_registry
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


async def _token_and_online_device(client: AsyncClient, slug: str, email: str) -> tuple[str, str, str]:
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
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "RpcDev", "device_type": "sensor"},
    )
    assert create.status_code == 201
    body = create.json()
    device_id = body["device"]["id"]
    tenant_id = body["device"]["tenant_id"]
    prov = await client.post(
        f"/api/v1/devices/{device_id}/provision",
        json={"provisioning_token": body["provisioning_token"]},
    )
    assert prov.status_code == 200
    creds = prov.json()
    import base64

    basic = base64.b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode()).decode()
    hb = await client.post(
        f"/api/v1/devices/{device_id}/heartbeat",
        headers={"Authorization": f"Basic {basic}"},
        json={},
    )
    assert hb.status_code == 200
    return token, device_id, tenant_id


@pytest.mark.asyncio
async def test_rpc_create_pending_then_delivered(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token, device_id, _ = await _token_and_online_device(client, unique_slug, unique_email)
    mock_pub = AsyncMock()
    app.state.mqtt_publisher = mock_pub
    with patch(
        "app.rpc.service.rpc_event_registry.register_wait",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.post(
            f"/api/v1/devices/{device_id}/rpc",
            headers={"Authorization": f"Bearer {token}"},
            json={"method": "reboot", "params": {}, "timeout_seconds": 1},
        )
    assert resp.status_code == 408
    mock_pub.publish_json.assert_awaited_once()
    async with async_session() as db:
        row = await db.scalar(
            select(DeviceRpcRequest).where(DeviceRpcRequest.device_id == uuid.UUID(device_id))
        )
    assert row is not None
    assert row.status in {DeviceRpcStatus.TIMEOUT, DeviceRpcStatus.DELIVERED}


@pytest.mark.asyncio
async def test_rpc_sync_wait_timeout_returns_408(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token, device_id, _ = await _token_and_online_device(client, unique_slug, unique_email)
    app.state.mqtt_publisher = AsyncMock()
    with patch(
        "app.rpc.service.rpc_event_registry.register_wait",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.post(
            f"/api/v1/devices/{device_id}/rpc",
            headers={"Authorization": f"Bearer {token}"},
            json={"method": "ping", "params": {}, "timeout_seconds": 1},
        )
    assert resp.status_code == 408
    assert resp.json()["status"] == "timeout"


@pytest.mark.asyncio
async def test_rpc_sync_wait_response_returns_200(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token, device_id, _ = await _token_and_online_device(client, unique_slug, unique_email)
    app.state.mqtt_publisher = AsyncMock()
    with patch(
        "app.rpc.service.rpc_event_registry.register_wait",
        new_callable=AsyncMock,
        return_value=RpcWaitResult(status="completed", response={"ok": True}, error=None),
    ):
        resp = await client.post(
            f"/api/v1/devices/{device_id}/rpc",
            headers={"Authorization": f"Bearer {token}"},
            json={"method": "get_sensor_reading", "params": {"id": 1}, "timeout_seconds": 5},
        )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    assert resp.json()["response"] == {"ok": True}


@pytest.mark.asyncio
async def test_rpc_device_offline_returns_503(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"T {unique_slug}",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "OfflineRpc", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    app.state.mqtt_publisher = AsyncMock()
    resp = await client.post(
        f"/api/v1/devices/{device_id}/rpc",
        headers={"Authorization": f"Bearer {token}"},
        json={"method": "reboot", "params": {}},
    )
    assert resp.status_code == 503
    assert resp.json()["reason"] == "device_offline"


@pytest.mark.asyncio
async def test_rpc_subscriber_resolves_pending_event(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    token, device_id, tenant_id = await _token_and_online_device(client, unique_slug, unique_email)
    request_id = uuid.uuid4()
    async with async_session() as db:
        db.add(
            DeviceRpcRequest(
                id=request_id,
                device_id=uuid.UUID(device_id),
                tenant_id=uuid.UUID(tenant_id),
                method="test",
                params={},
                status=DeviceRpcStatus.DELIVERED,
                timeout_seconds=30,
            )
        )
        await db.commit()
    wait_task = asyncio.create_task(
        rpc_event_registry.register_wait(request_id, timeout_seconds=2.0)
    )
    await asyncio.sleep(0.05)
    message = MagicMock()
    message.topic = f"tenants/{tenant_id}/devices/{device_id}/commands/{request_id}/response"
    message.payload = b'{"status":"ok","data":{"temp":25}}'
    await MqttSubscriberService(test_redis)._handle_rpc_response(message, message.topic)
    result = await wait_task
    assert result is not None
    assert result.response == {"temp": 25}


@pytest.mark.asyncio
async def test_rpc_subscriber_ignores_unknown_request_id(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    token, device_id, tenant_id = await _token_and_online_device(client, unique_slug, unique_email)
    unknown = uuid.uuid4()
    message = MagicMock()
    message.topic = f"tenants/{tenant_id}/devices/{device_id}/commands/{unknown}/response"
    message.payload = b'{"status":"ok","data":{}}'
    await MqttSubscriberService(test_redis)._handle_rpc_response(message, message.topic)


@pytest.mark.asyncio
async def test_rpc_history_list(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token, device_id, tenant_id = await _token_and_online_device(client, unique_slug, unique_email)
    async with async_session() as db:
        db.add(
            DeviceRpcRequest(
                device_id=uuid.UUID(device_id),
                tenant_id=uuid.UUID(tenant_id),
                method="hist",
                params={"a": 1},
                status=DeviceRpcStatus.COMPLETED,
                timeout_seconds=30,
            )
        )
        await db.commit()
    resp = await client.get(
        f"/api/v1/devices/{device_id}/rpc",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()["items"]) >= 1


@pytest.mark.asyncio
async def test_rpc_history_filter_by_status(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token, device_id, tenant_id = await _token_and_online_device(client, unique_slug, unique_email)
    async with async_session() as db:
        db.add(
            DeviceRpcRequest(
                device_id=uuid.UUID(device_id),
                tenant_id=uuid.UUID(tenant_id),
                method="pending_one",
                params={},
                status=DeviceRpcStatus.PENDING,
                timeout_seconds=30,
            )
        )
        await db.commit()
    resp = await client.get(
        f"/api/v1/devices/{device_id}/rpc",
        headers={"Authorization": f"Bearer {token}"},
        params={"status": "pending"},
    )
    assert resp.status_code == 200
    assert all(item["status"] == "pending" for item in resp.json()["items"])


@pytest.mark.asyncio
async def test_rpc_timeout_updates_status_in_db(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token, device_id, _ = await _token_and_online_device(client, unique_slug, unique_email)
    app.state.mqtt_publisher = AsyncMock()
    with patch(
        "app.rpc.service.rpc_event_registry.register_wait",
        new_callable=AsyncMock,
        return_value=None,
    ):
        await client.post(
            f"/api/v1/devices/{device_id}/rpc",
            headers={"Authorization": f"Bearer {token}"},
            json={"method": "slow", "params": {}, "timeout_seconds": 1},
        )
    async with async_session() as db:
        row = await db.scalar(
            select(DeviceRpcRequest).where(DeviceRpcRequest.device_id == uuid.UUID(device_id))
        )
    assert row is not None
    assert row.status == DeviceRpcStatus.TIMEOUT


@pytest.mark.asyncio
async def test_rpc_params_arbitrary_json_passthrough(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token, device_id, _ = await _token_and_online_device(client, unique_slug, unique_email)
    captured: list[dict[str, object]] = []
    pub = AsyncMock()

    async def _capture(topic: str, payload: dict[str, object], qos: int = 1) -> None:
        captured.append(payload)

    pub.publish_json = _capture
    app.state.mqtt_publisher = pub
    params = {"nested": {"list": [1, 2]}, "flag": True, "label": "x"}
    with patch(
        "app.rpc.service.rpc_event_registry.register_wait",
        new_callable=AsyncMock,
        return_value=None,
    ):
        await client.post(
            f"/api/v1/devices/{device_id}/rpc",
            headers={"Authorization": f"Bearer {token}"},
            json={"method": "configure", "params": params, "timeout_seconds": 1},
        )
    assert captured
    assert captured[0]["params"] == params
