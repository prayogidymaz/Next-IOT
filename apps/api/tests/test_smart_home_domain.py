import pytest
from app.models.device_category import DeviceCategory, infer_device_category
from app.telemetry.smart_home_metrics import normalize_telemetry_metrics
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


def test_infer_device_category_smart_home():
    assert infer_device_category("smart_home") == DeviceCategory.SMART_HOME
    assert infer_device_category("smart-home") == DeviceCategory.SMART_HOME


def test_normalize_smart_home_metrics():
    metrics = normalize_telemetry_metrics(
        {
            "relay_state": "on",
            "pir_motion": 1,
            "hvac_temp": 22.5,
            "lock_state": "locked",
        }
    )
    assert metrics["relay_state"] == "ON"
    assert metrics["pir_motion"] is True
    assert metrics["hvac_temp"] == 22.5
    assert metrics["lock_state"] == "LOCKED"


@pytest.mark.asyncio
async def test_register_device_with_smart_home_category(
    client: AsyncClient, unique_slug: str, unique_email: str
):
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"T {unique_slug}",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    assert reg.status_code == 201
    token = reg.json()["tokens"]["access_token"]

    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Lobby Relay",
            "device_type": "smart_home",
            "device_category": "SMART_HOME",
        },
    )
    assert create.status_code == 201
    body = create.json()["device"]
    assert body["device_category"] == "SMART_HOME"
    assert body["device_type"] == "smart_home"


async def _register_provision_online(client: AsyncClient, slug: str, email: str) -> dict:
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
        json={"name": "Smart Node", "device_type": "smart_home"},
    )
    body = create.json()
    device_id = body["device"]["id"]
    prov = await client.post(
        f"/api/v1/devices/{device_id}/provision",
        json={"provisioning_token": body["provisioning_token"]},
    )
    creds = prov.json()

    import base64

    basic = base64.b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode()).decode()
    device_headers = {"Authorization": f"Basic {basic}"}

    hb = await client.post(f"/api/v1/devices/{device_id}/heartbeat", headers=device_headers, json={})
    assert hb.status_code == 200

    return {
        "device_id": device_id,
        "device_headers": device_headers,
    }


@pytest.mark.asyncio
async def test_smart_home_telemetry_ingest(client: AsyncClient, unique_slug: str, unique_email: str):
    from datetime import UTC, datetime

    ctx = await _register_provision_online(client, unique_slug, unique_email)
    ts = datetime.now(UTC).isoformat()

    resp = await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={
            "timestamp": ts,
            "metrics": {
                "relay_state": "ON",
                "pir_motion": True,
                "hvac_temp": 23.5,
                "lock_state": "LOCKED",
            },
        },
    )
    assert resp.status_code == 201
    metrics = resp.json()["metrics"]
    assert metrics["relay_state"] == "ON"
    assert metrics["pir_motion"] is True
    assert metrics["hvac_temp"] == 23.5
    assert metrics["lock_state"] == "LOCKED"
