"""Irrigation valve tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from tests.agriculture.conftest import auth, create_farm, create_plot, register_tenant


@pytest.mark.asyncio
async def test_valve_control_and_schedule(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    reg = await register_tenant(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    farm = await create_farm(client, token)
    plot = await create_plot(client, token, str(farm["id"]))
    valve = await client.post(
        f"/api/agriculture/plots/{plot['id']}/valves",
        headers=auth(token),
        json={"name": "V1", "flow_rate_lpm": "25"},
    )
    assert valve.status_code == 201
    valve_id = valve.json()["id"]
    opened = await client.post(
        f"/api/agriculture/valves/{valve_id}/open",
        headers=auth(token),
        json={"duration_minutes": 10},
    )
    assert opened.status_code == 200
    closed = await client.post(f"/api/agriculture/valves/{valve_id}/close", headers=auth(token))
    assert closed.status_code == 200
    sched = await client.put(
        f"/api/agriculture/valves/{valve_id}/schedule",
        headers=auth(token),
        json={"schedule": {"cron": "0 6 * * *"}},
    )
    assert sched.status_code == 200
    auto = await client.post(f"/api/agriculture/farms/{farm['id']}/irrigation/auto-run", headers=auth(token))
    assert auto.status_code == 200
