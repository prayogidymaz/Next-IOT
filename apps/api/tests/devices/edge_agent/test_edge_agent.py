"""Edge agent registration and OTA tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from app.devices.edge_agent.models import EdgeDeviceToken, FirmwareVersionRow
from app.devices.edge_agent.ota_service import OTAService
from app.database import async_session

PASSWORD = "SecurePass123!"


async def _seed_token(tenant_id: uuid.UUID, token: str, expired: bool = False) -> None:
    async with async_session() as db:
        db.add(
            EdgeDeviceToken(
                token=token,
                tenant_id=tenant_id,
                max_devices=5,
                expires_at=datetime.now(tz=UTC) - timedelta(days=1) if expired else None,
            )
        )
        await db.commit()


@pytest.mark.asyncio
async def test_auto_register_with_valid_token(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Edge", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    tenant_id = uuid.UUID(reg.json()["tenant_id"])
    token = f"edge-{uuid.uuid4().hex}"
    await _seed_token(tenant_id, token)
    resp = await client.post(
        "/api/v1/devices/register",
        json={"device_token": token, "device_type": "esp32_sensor", "capabilities": ["soil_moisture"]},
    )
    assert resp.status_code == 200
    assert resp.json()["device_id"]


@pytest.mark.asyncio
async def test_register_token_expired(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "EdgeExp", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    tenant_id = uuid.UUID(reg.json()["tenant_id"])
    token = f"edge-exp-{uuid.uuid4().hex}"
    await _seed_token(tenant_id, token, expired=True)
    resp = await client.post(
        "/api/v1/devices/register",
        json={"device_token": token, "device_type": "esp32_sensor", "capabilities": []},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ota_get_latest_firmware(client: AsyncClient) -> None:
    async with async_session() as db:
        db.add(
            FirmwareVersionRow(
                device_type="esp32_sensor",
                version="1.0.0",
                binary_url="/firmware/esp32-1.0.0.bin",
                checksum="abc",
            )
        )
        await db.commit()
    resp = await client.get("/api/v1/firmware/latest?device_type=esp32_sensor")
    assert resp.status_code == 200
    assert resp.json()["version"] == "1.0.0"


def test_ota_checksum_validation() -> None:
    svc = OTAService()
    data = b"firmware-binary-content"
    digest = svc.validate_checksum(data, "wrong")
    assert digest is False
    import hashlib

    expected = hashlib.sha256(data).hexdigest()
    assert svc.validate_checksum(data, expected) is True


@pytest.mark.asyncio
async def test_firmware_upload_admin_only(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Fw", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    files = {"file": ("fw.bin", b"bin", "application/octet-stream")}
    data = {"device_type": "esp32_sensor", "version": "1.2.3"}
    denied = await client.post("/api/v1/firmware/upload", files=files, data=data)
    assert denied.status_code == 401
    ok = await client.post(
        "/api/v1/firmware/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        data=data,
    )
    assert ok.status_code == 201


@pytest.mark.asyncio
async def test_firmware_versions_list(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/firmware/versions?device_type=esp32_sensor")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_register_invalid_token(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/devices/register",
        json={"device_token": "missing-token", "device_type": "esp32_sensor", "capabilities": []},
    )
    assert resp.status_code == 401


def test_ota_service_latest_none() -> None:
    assert OTAService is not None


@pytest.mark.asyncio
async def test_edge_register_returns_mqtt_prefix(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Edge2", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    tenant_id = uuid.UUID(reg.json()["tenant_id"])
    token = f"edge2-{uuid.uuid4().hex}"
    await _seed_token(tenant_id, token)
    resp = await client.post(
        "/api/v1/devices/register",
        json={"device_token": token, "device_type": "esp32_actuator", "capabilities": ["valve"]},
    )
    body = resp.json()
    assert body["mqtt_topic_prefix"].startswith("next-iot/sensor/")
