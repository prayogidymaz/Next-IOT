"""Firmware Studio generator tests."""

from __future__ import annotations

import io
import uuid
import zipfile

import pytest
from app.firmware_studio.generator import build_firmware_zip, render_preview
from app.firmware_studio.schemas import FirmwareStudioConfig, SensorBinding
from app.firmware_studio.sensor_drivers import catalog_public
from app.models.device_profile import DeviceProfile, ProfileDomain, ProfileStatus
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


def _sample_config(**overrides: object) -> FirmwareStudioConfig:
    base = {
        "wifi_ssid": "TestWifi",
        "wifi_password": "testpass",
        "broker_host": "192.168.1.100",
        "publish_interval_s": 10,
        "sensors": [
            SensorBinding(metric="temperature", driver="dht22", pin=4),
            SensorBinding(metric="humidity", driver="dht22", pin=4),
        ],
    }
    base.update(overrides)
    return FirmwareStudioConfig.model_validate(base)


def _sample_profile() -> DeviceProfile:
    tenant_id = uuid.uuid4()
    return DeviceProfile(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        key="pond_sensor",
        name="Pond Sensor",
        description="test",
        domain=ProfileDomain.SMART_FARMING.value,
        version=1,
        status=ProfileStatus.PUBLISHED.value,
        spec={
            "telemetry": [
                {"key": "temperature", "label": "Temp", "data_type": "number"},
                {"key": "humidity", "label": "Hum", "data_type": "number"},
            ],
            "attributes": [],
            "commands": [],
        },
    )


def test_sensor_drivers_catalog() -> None:
    catalog = catalog_public()
    assert "temperature" in catalog
    assert "dht22" in catalog["temperature"]


def test_generate_platformio_ini_valid() -> None:
    preview = render_preview(_sample_profile(), _sample_config())
    assert "[env:esp32-s3]" in preview.platformio_ini
    assert "PubSubClient" in preview.platformio_ini


def test_generate_main_cpp_includes_metric_sensors() -> None:
    preview = render_preview(_sample_profile(), _sample_config())
    assert "temperature" in preview.main_cpp
    assert "humidity" in preview.main_cpp
    assert "dhtSensor.readTemperature()" in preview.main_cpp


def test_generate_with_ota_enabled_includes_ota_code() -> None:
    preview = render_preview(_sample_profile(), _sample_config(enable_ota=True))
    assert "enableOta()" in preview.main_cpp


def test_generate_without_credentials_mode() -> None:
    preview = render_preview(_sample_profile(), _sample_config(include_credentials=False))
    assert "YOUR_TENANT_ID" in preview.main_cpp
    assert "YOUR_ACCESS_TOKEN" in preview.main_cpp


def test_generate_with_credentials_mode() -> None:
    tid = uuid.uuid4()
    did = uuid.uuid4()
    preview = render_preview(
        _sample_profile(),
        _sample_config(
            include_credentials=True,
            tenant_id=tid,
            device_id=did,
            access_token="tok123",
        ),
    )
    assert str(tid) in preview.main_cpp
    assert "tok123" in preview.main_cpp


def test_generate_handles_multiple_metrics() -> None:
    zip_bytes = build_firmware_zip(_sample_profile(), _sample_config())
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        main_cpp = zf.read("src/main.cpp").decode()
    assert "temperature" in main_cpp and "humidity" in main_cpp


def test_generate_includes_sdk_source() -> None:
    zip_bytes = build_firmware_zip(_sample_profile(), _sample_config())
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
    assert any(n.endswith("NextIotClient.h") for n in names)


def test_generate_zip_structure_correct() -> None:
    zip_bytes = build_firmware_zip(_sample_profile(), _sample_config())
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = set(zf.namelist())
    assert "platformio.ini" in names
    assert "src/main.cpp" in names
    assert "README.md" in names


def test_generate_rejects_invalid_sensor_driver() -> None:
    config = _sample_config(sensors=[SensorBinding(metric="temperature", driver="invalid_x", pin=1)])
    with pytest.raises(ValueError):
        build_firmware_zip(_sample_profile(), config)


@pytest.mark.asyncio
async def test_generate_requires_device_profile(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
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
    missing = await client.post(
        "/api/v1/firmware-studio/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "device_profile_id": str(uuid.uuid4()),
            "config": _sample_config().model_dump(mode="json"),
        },
    )
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_generate_api_returns_zip(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
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
    create_profile = await client.post(
        "/api/v1/device-profiles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "key": "pond_sensor",
            "name": "Pond Sensor",
            "description": "test",
            "domain": "smart_farming",
            "spec": _sample_profile().spec,
        },
    )
    assert create_profile.status_code == 201
    profile_id = create_profile.json()["id"]

    resp = await client.post(
        "/api/v1/firmware-studio/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "device_profile_id": str(profile_id),
            "config": _sample_config().model_dump(mode="json"),
        },
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        assert "src/main.cpp" in zf.namelist()
