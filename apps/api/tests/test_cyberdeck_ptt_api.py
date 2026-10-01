import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _token(client: AsyncClient, slug: str, email: str) -> str:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    return reg.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_cyberdeck_mesh_returns_nodes(client: AsyncClient, unique_slug: str, unique_email: str):
    token = await _token(client, unique_slug, unique_email)
    resp = await client.get(
        "/api/v1/hardware/cyberdeck/mesh",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 3
    assert any(n["node_id"] == "CDK-01" for n in data["nodes"])


@pytest.mark.asyncio
async def test_cyberdeck_ptt_text_dispatch(client: AsyncClient, unique_slug: str, unique_email: str):
    token = await _token(client, unique_slug, unique_email)
    resp = await client.post(
        "/api/v1/hardware/cyberdeck/ptt/text",
        headers={"Authorization": f"Bearer {token}"},
        json={"channel": 2, "message": "RTB grid alpha", "encrypt": True, "target_node_id": "CDK-02"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["ok"] is True
    assert body["channel"] == 2
    assert body["encrypted"] is True
