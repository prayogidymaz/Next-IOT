import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _setup_device_with_signal_telemetry(client: AsyncClient, slug: str, email: str) -> dict:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "LoRa Node", "device_type": "drone"},
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
    await client.post(f"/api/v1/devices/{device_id}/heartbeat", headers=device_headers, json={})

    now = datetime.now(UTC)
    samples = [
        (-6.2088, 106.8456, -80.0, 10.0),
        (-6.2095, 106.8465, -92.0, 8.0),
        (-6.2102, 106.8472, -110.0, 4.5),
    ]
    for index, (lat, lon, rssi, snr) in enumerate(samples):
        ts = (now - timedelta(minutes=30 - index * 5)).isoformat()
        await client.post(
            "/api/v1/telemetry",
            headers=device_headers,
            json={
                "timestamp": ts,
                "metrics": {
                    "latitude": lat,
                    "longitude": lon,
                    "rssi": rssi,
                    "snr": snr,
                },
            },
        )

    return {"user_token": token, "device_id": device_id}


@pytest.mark.asyncio
async def test_signal_heatmap_returns_gps_rssi_points(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device_with_signal_telemetry(client, unique_slug, unique_email)

    resp = await client.get(
        "/api/v1/telemetry/signal-heatmap",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"device_id": ctx["device_id"], "hours": 24},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 3
    assert len(data["points"]) == 3
    assert data["points"][0]["signal_strength"] == "strong"
    assert data["points"][1]["signal_strength"] == "marginal"
    assert data["points"][2]["signal_strength"] == "weak"
    assert data["points"][0]["signal_score"] >= 80
    assert data["points"][2]["signal_score"] <= 39


@pytest.mark.asyncio
async def test_signal_heatmap_hours_validation(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device_with_signal_telemetry(client, unique_slug, unique_email)

    resp = await client.get(
        "/api/v1/telemetry/signal-heatmap",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"device_id": ctx["device_id"], "hours": 6},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_signal_heatmap_tenant_isolation(client: AsyncClient):
    slug_a = f"a-{uuid.uuid4().hex[:6]}"
    slug_b = f"b-{uuid.uuid4().hex[:6]}"
    ctx_a = await _setup_device_with_signal_telemetry(client, slug_a, f"a-{uuid.uuid4().hex[:6]}@example.com")
    ctx_b = await _setup_device_with_signal_telemetry(client, slug_b, f"b-{uuid.uuid4().hex[:6]}@example.com")

    denied = await client.get(
        "/api/v1/telemetry/signal-heatmap",
        headers={"Authorization": f"Bearer {ctx_a['user_token']}"},
        params={"device_id": ctx_b["device_id"], "hours": 1},
    )
    assert denied.status_code == 404
