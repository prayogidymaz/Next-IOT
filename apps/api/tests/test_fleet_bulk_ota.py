import io

import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _tenant_token(client: AsyncClient, unique_slug: str, unique_email: str) -> str:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"Fleet {unique_slug}",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    assert reg.status_code == 201
    return reg.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_bulk_import_json(client: AsyncClient, unique_slug: str, unique_email: str):
    token = await _tenant_token(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "devices": [
            {"name": "Bulk Node A", "device_type": "sensor"},
            {"name": "Bulk Node B", "device_type": "lorawan", "device_category": "FIELD_SENSORS_LORA"},
        ]
    }
    resp = await client.post("/api/v1/devices/bulk-import", headers=headers, json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["imported_count"] == 2
    assert body["failed_count"] == 0
    assert len(body["items"]) == 2


@pytest.mark.asyncio
async def test_bulk_import_csv_multipart(client: AsyncClient, unique_slug: str, unique_email: str):
    token = await _tenant_token(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {token}"}

    csv_data = "name,device_type,device_category\nCSV One,sensor,\nCSV Two,smart_home,SMART_HOME\n"
    files = {"file": ("devices.csv", io.BytesIO(csv_data.encode()), "text/csv")}
    resp = await client.post("/api/v1/devices/bulk-import", headers=headers, files=files)
    assert resp.status_code == 201
    body = resp.json()
    assert body["imported_count"] == 2


@pytest.mark.asyncio
async def test_ota_upload_publish_and_device_check(client: AsyncClient, unique_slug: str, unique_email: str):
    token = await _tenant_token(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {token}"}

    reg = await client.post(
        "/api/v1/devices",
        headers=headers,
        json={"name": "OTA Target", "device_type": "sensor", "device_category": "FIELD_SENSORS_LORA"},
    )
    assert reg.status_code == 201
    device_id = reg.json()["device"]["id"]
    prov_token = reg.json()["provisioning_token"]

    creds = await client.post(f"/api/v1/devices/{device_id}/provision", json={"provisioning_token": prov_token})
    assert creds.status_code == 200
    client_id = creds.json()["client_id"]
    client_secret = creds.json()["client_secret"]
    device_auth = (client_id, client_secret)

    firmware = b"\x00\x01\x02fake-firmware"
    files = {"file": ("fw.bin", io.BytesIO(firmware), "application/octet-stream")}
    data = {"version": "1.0.0", "target_device_category": "FIELD_SENSORS_LORA"}
    upload = await client.post("/api/v1/ota/releases", headers=headers, files=files, data=data)
    assert upload.status_code == 201
    release_id = upload.json()["id"]

    publish = await client.post(f"/api/v1/ota/releases/{release_id}/publish", headers=headers)
    assert publish.status_code == 200
    assert publish.json()["targeted_devices"] >= 1

    check = await client.get(
        "/api/v1/ota/check",
        auth=device_auth,
        params={"current_version": "0.9.0"},
    )
    assert check.status_code == 200
    assert check.json()["update_available"] is True
    assert check.json()["version"] == "1.0.0"

    rollouts = await client.get(f"/api/v1/ota/releases/{release_id}/rollouts", headers=headers)
    assert rollouts.status_code == 200
    assert len(rollouts.json()) >= 1
