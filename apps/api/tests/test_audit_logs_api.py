import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _register_admin(client: AsyncClient, slug: str, email: str) -> str:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    assert reg.status_code == 201
    return reg.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_login_creates_audit_log(client: AsyncClient, unique_slug: str, unique_email: str):
    token = await _register_admin(client, unique_slug, unique_email)
    await client.post("/auth/login", json={"email": unique_email, "password": PASSWORD})

    resp = await client.get(
        "/api/v1/audit-logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    actions = {item["action"] for item in body["items"]}
    assert "LOGIN" in actions


@pytest.mark.asyncio
async def test_viewer_cannot_read_audit_logs(client: AsyncClient, unique_slug: str, unique_email: str):
    admin_token = await _register_admin(client, unique_slug, unique_email)
    tenant_id = (
        await client.get("/api/v1/me", headers={"Authorization": f"Bearer {admin_token}"})
    ).json()["tenant_id"]

    viewer_email = f"viewer_{unique_email}"
    invite = await client.post(
        f"/api/v1/tenants/{tenant_id}/members",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"email": viewer_email, "password": PASSWORD, "role": "viewer"},
    )
    assert invite.status_code == 201

    login = await client.post("/auth/login", json={"email": viewer_email, "password": PASSWORD})
    viewer_token = login.json()["access_token"]

    resp = await client.get(
        "/api/v1/audit-logs",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_audit_log_export_csv(client: AsyncClient, unique_slug: str, unique_email: str):
    token = await _register_admin(client, unique_slug, unique_email)
    await client.post("/auth/login", json={"email": unique_email, "password": PASSWORD})

    resp = await client.get(
        "/api/v1/audit-logs/export",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
    assert "timestamp,actor_id" in resp.text.splitlines()[0]
