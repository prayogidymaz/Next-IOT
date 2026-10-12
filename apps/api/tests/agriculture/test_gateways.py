"""Gateway tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from tests.agriculture.conftest import auth, create_farm, register_tenant


@pytest.mark.asyncio
async def test_gateway_crud_stats(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await register_tenant(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    farm = await create_farm(client, token)
    created = await client.post(
        "/api/agriculture/gateways",
        headers=auth(token),
        json={"farm_id": farm["id"], "name": "GW-1", "gateway_eui": "GW00112233445566"},
    )
    assert created.status_code == 201
    gw_id = created.json()["id"]
    stats = await client.get(f"/api/agriculture/gateways/{gw_id}/stats", headers=auth(token))
    assert stats.status_code == 200
    listed = await client.get("/api/agriculture/gateways", headers=auth(token))
    assert listed.status_code == 200
