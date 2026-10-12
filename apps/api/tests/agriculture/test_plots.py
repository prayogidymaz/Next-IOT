"""Plot tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from tests.agriculture.conftest import auth, create_farm, create_plot, register_tenant


@pytest.mark.asyncio
async def test_plot_crud_and_heatmap(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await register_tenant(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    farm = await create_farm(client, token)
    plot = await create_plot(client, token, str(farm["id"]))
    plot_id = plot["id"]
    detail = await client.get(f"/api/agriculture/plots/{plot_id}", headers=auth(token))
    assert detail.status_code == 200
    heat = await client.get(f"/api/agriculture/plots/{plot_id}/heatmap", headers=auth(token))
    assert heat.status_code == 200
    assert len(heat.json()) >= 1
    upd = await client.put(
        f"/api/agriculture/plots/{plot_id}",
        headers=auth(token),
        json={"crop_variety": "Arabika"},
    )
    assert upd.status_code == 200
