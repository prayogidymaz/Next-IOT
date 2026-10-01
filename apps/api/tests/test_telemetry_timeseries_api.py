import base64
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _seed_temperature_series(client: AsyncClient, slug: str, email: str) -> dict:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Sensor", "device_type": "sensor"},
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

    now = datetime.now(UTC)
    for i, temp in enumerate([22.0, 24.0, 31.0, 28.0]):
        await client.post(
            "/api/v1/telemetry",
            headers=device_headers,
            json={
                "timestamp": (now - timedelta(minutes=30 - i * 5)).isoformat(),
                "metrics": {"temperature": temp, "humidity": 60 + i},
            },
        )

    return {"token": token, "device_id": device_id}


@pytest.mark.asyncio
async def test_analytics_timeseries_buckets(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _seed_temperature_series(client, unique_slug, unique_email)
    end = datetime.now(UTC)
    start = end - timedelta(hours=1)
    resp = await client.get(
        "/api/v1/telemetry/analytics",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        params={
            "device_id": ctx["device_id"],
            "metrics": "temperature,humidity",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "interval": "5m",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["reading_count"] == 4
    assert len(body["series"]) == 2
    temp = next(s for s in body["series"] if s["metric"] == "temperature")
    assert temp["stats"]["max"] == 31.0
    assert temp["stats"]["latest"] == 28.0
    assert len(temp["points"]) >= 1
