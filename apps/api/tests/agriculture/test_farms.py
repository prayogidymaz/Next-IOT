"""Farm CRUD tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from tests.agriculture.conftest import auth, create_farm, register_tenant


@pytest.mark.asyncio
async def test_farm_crud_and_overview(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await register_tenant(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    farm = await create_farm(client, token)
    farm_id = farm["id"]
    got = await client.get(f"/api/agriculture/farms/{farm_id}", headers=auth(token))
    assert got.status_code == 200
    updated = await client.put(
        f"/api/agriculture/farms/{farm_id}",
        headers=auth(token),
        json={"owner_whatsapp": "628111"},
    )
    assert updated.status_code == 200
    overview = await client.get(f"/api/agriculture/farms/{farm_id}/overview", headers=auth(token))
    assert overview.status_code == 200
    assert overview.json()["sensor_count"] == 0
    deleted = await client.delete(f"/api/agriculture/farms/{farm_id}", headers=auth(token))
    assert deleted.status_code == 204


@pytest.mark.asyncio
async def test_farm_tenant_isolation(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg_a = await register_tenant(client, unique_slug, unique_email)
    token_a = str(reg_a["tokens"]["access_token"])
    farm = await create_farm(client, token_a)
    reg_b = await register_tenant(client, f"{unique_slug}-b", f"b-{unique_email}")
    token_b = str(reg_b["tokens"]["access_token"])
    foreign = await client.get(f"/api/agriculture/farms/{farm['id']}", headers=auth(token_b))
    assert foreign.status_code == 404


@pytest.mark.asyncio
async def test_farm_list_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/agriculture/farms")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_farm_unauthorized_delete(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await register_tenant(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    farm = await create_farm(client, token)
    resp = await client.delete(f"/api/agriculture/farms/{farm['id']}")
    assert resp.status_code == 401
