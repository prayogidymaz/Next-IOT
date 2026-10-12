"""Agriculture test helpers."""

from __future__ import annotations

from httpx import AsyncClient


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def register_tenant(client: AsyncClient, slug: str, email: str) -> dict[str, object]:
    resp = await client.post(
        "/auth/register",
        json={"tenant_name": slug, "tenant_slug": slug, "email": email, "password": "TestPass123!"},
    )
    assert resp.status_code == 201
    return resp.json()


async def create_farm(client: AsyncClient, token: str, name: str = "Kebun Test") -> dict[str, object]:
    resp = await client.post(
        "/api/agriculture/farms",
        headers=auth(token),
        json={"name": name, "crop_type": "coffee", "area_hectares": "2.5"},
    )
    assert resp.status_code == 201
    return resp.json()


async def create_plot(client: AsyncClient, token: str, farm_id: str, name: str = "Blok A") -> dict[str, object]:
    resp = await client.post(
        f"/api/agriculture/farms/{farm_id}/plots",
        headers=auth(token),
        json={"name": name, "area_hectares": "1.0"},
    )
    assert resp.status_code == 201
    return resp.json()
