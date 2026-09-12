import base64
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _setup_device(client: AsyncClient, slug: str, email: str) -> dict:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Replay Drone", "device_type": "drone"},
    )
    body = create.json()
    device_id = body["device"]["id"]
    prov = await client.post(
        f"/api/v1/devices/{device_id}/provision",
        json={"provisioning_token": body["provisioning_token"]},
    )
    creds = prov.json()
    basic = base64.b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode()).decode()
    device_headers = {"Authorization": f"Basic {basic}"}
    await client.post(f"/api/v1/devices/{device_id}/heartbeat", headers=device_headers, json={})
    return {"user_token": token, "device_id": device_id, "device_headers": device_headers}


@pytest.mark.asyncio
async def test_flight_replay_returns_chronological_samples(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device(client, unique_slug, unique_email)
    now = datetime.now(UTC)

    for i in range(3):
        await client.post(
            "/api/v1/telemetry",
            headers=ctx["device_headers"],
            json={
                "timestamp": (now - timedelta(minutes=10 - i * 2)).isoformat(),
                "metrics": {
                    "latitude": -6.2088 + i * 0.001,
                    "longitude": 106.8456 + i * 0.001,
                    "altitude_m": 50 + i,
                    "speed": 10 + i,
                    "yaw": 90 + i,
                    "rssi": -80 - i,
                },
            },
        )

    resp = await client.get(
        "/api/v1/telemetry/flight-replay",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"device_id": ctx["device_id"], "hours": 24},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] >= 3
    assert len(body["samples"]) >= 3
    assert body["samples"][0]["lat"] == pytest.approx(-6.2088, abs=0.001)
    assert body["samples"][-1]["speed"] is not None


@pytest.mark.asyncio
async def test_flight_replay_includes_anomalies(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device(client, unique_slug, unique_email)
    now = datetime.now(UTC)

    await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "metrics": {"latitude": -6.2, "longitude": 106.84, "voltage": 12.0, "temperature": 30},
        },
    )
    await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={
            "timestamp": now.isoformat(),
            "metrics": {"latitude": -6.21, "longitude": 106.85, "voltage": 8.0, "temperature": 30},
        },
    )

    resp = await client.get(
        "/api/v1/telemetry/flight-replay",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"device_id": ctx["device_id"], "hours": 1},
    )
    assert resp.status_code == 200
    samples_with_anomaly = [s for s in resp.json()["samples"] if s["anomalies"]]
    assert len(samples_with_anomaly) >= 1


@pytest.mark.asyncio
async def test_flight_replay_hours_validation(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device(client, unique_slug, unique_email)
    resp = await client.get(
        "/api/v1/telemetry/flight-replay",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"device_id": ctx["device_id"], "hours": 48},
    )
    assert resp.status_code == 422
