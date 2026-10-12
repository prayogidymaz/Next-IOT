"""Additional endpoint matrix for coverage."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from tests.agriculture.conftest import auth, create_farm, create_plot, register_tenant

CROP_TYPES = ["coffee", "oil_palm", "rice", "horticulture", "cocoa", "pepper", "other"]


@pytest.mark.asyncio
@pytest.mark.parametrize("crop", CROP_TYPES)
async def test_create_farm_crop_types(client: AsyncClient, unique_slug: str, unique_email: str, crop: str) -> None:
    slug = f"{unique_slug}-{crop.replace('_', '-')}"
    reg = await register_tenant(client, slug, f"{crop}-{unique_email}")
    token = str(reg["tokens"]["access_token"])
    resp = await client.post(
        "/api/agriculture/farms",
        headers=auth(token),
        json={"name": f"Farm {crop}", "crop_type": crop},
    )
    assert resp.status_code == 201
    assert resp.json()["crop_type"] == crop


@pytest.mark.asyncio
async def test_list_farms_after_create(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await register_tenant(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    await create_farm(client, token, "A")
    await create_farm(client, token, "B")
    listed = await client.get("/api/agriculture/farms", headers=auth(token))
    assert listed.status_code == 200
    assert len(listed.json()) >= 2


@pytest.mark.asyncio
async def test_plot_list_on_farm(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await register_tenant(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    farm = await create_farm(client, token)
    await create_plot(client, token, str(farm["id"]), "P1")
    plots = await client.get(f"/api/agriculture/farms/{farm['id']}/plots", headers=auth(token))
    assert plots.status_code == 200
    assert len(plots.json()) == 1
