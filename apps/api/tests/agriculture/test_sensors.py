"""Sensor commission tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from tests.agriculture.conftest import auth, create_farm, create_plot, register_tenant


@pytest.mark.asyncio
async def test_sensor_commission_calibrate(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await register_tenant(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    farm = await create_farm(client, token)
    plot = await create_plot(client, token, str(farm["id"]))
    created = await client.post(
        f"/api/agriculture/farms/{farm['id']}/sensors",
        headers=auth(token),
        json={
            "name": "Soil-1",
            "sensor_type": "soil_moisture",
            "lora_dev_eui": "A1B2C3D4E5F6A7B8",
            "lora_app_key": "00112233445566778899AABBCCDDEEFF",
            "plot_id": plot["id"],
        },
    )
    assert created.status_code == 201
    sensor_id = created.json()["id"]
    readings = await client.get(f"/api/agriculture/sensors/{sensor_id}/readings", headers=auth(token))
    assert readings.status_code == 200
    cal = await client.post(
        f"/api/agriculture/sensors/{sensor_id}/calibrate",
        headers=auth(token),
        json={"offsets": {"moisture": 2.5}},
    )
    assert cal.status_code == 200
    batt = await client.get(f"/api/agriculture/sensors/{sensor_id}/battery-history", headers=auth(token))
    assert batt.status_code == 200
