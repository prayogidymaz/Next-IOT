import uuid

import pytest
from app.auth.security import hash_password
from app.database import async_session
from app.models.tenant_membership import TenantMembership
from app.models.user import User
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _register(client: AsyncClient, slug: str, email: str) -> dict:
    resp = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"Tenant {slug}",
            "tenant_slug": slug,
            "email": email,
            "password": PASSWORD,
        },
    )
    assert resp.status_code == 201
    return resp.json()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_tenants_after_register(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]

    resp = await client.get("/api/v1/tenants", headers=_auth(token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any(t["slug"] == unique_slug for t in data)


@pytest.mark.asyncio
async def test_me_permissions_tenant_admin(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]

    resp = await client.get("/api/v1/users/me/permissions", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "tenant_admin"
    assert "devices.register" in body["permissions"]
    assert "tenant.manage" in body["permissions"]


@pytest.mark.asyncio
async def test_viewer_permissions_limited(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(reg["tenant_id"])
    admin_token = reg["tokens"]["access_token"]

    viewer_email = f"viewer-{uuid.uuid4().hex[:6]}@example.com"
    async with async_session() as session:
        viewer = User(
            tenant_id=tenant_id,
            email=viewer_email,
            password_hash=hash_password(PASSWORD),
            role="viewer",
        )
        session.add(viewer)
        await session.flush()
        session.add(
            TenantMembership(user_id=viewer.id, tenant_id=tenant_id, role="viewer")
        )
        await session.commit()

    login = await client.post(
        "/auth/login",
        json={"email": viewer_email, "password": PASSWORD},
    )
    token = login.json()["access_token"]

    resp = await client.get("/api/v1/users/me/permissions", headers=_auth(token))
    assert resp.status_code == 200
    perms = set(resp.json()["permissions"])
    assert "devices.read" in perms
    assert "devices.register" not in perms
    assert "commands.send" not in perms


@pytest.mark.asyncio
async def test_tenant_admin_can_create_tenant(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]
    new_slug = f"child-{uuid.uuid4().hex[:8]}"

    resp = await client.post(
        "/api/v1/tenants",
        headers=_auth(token),
        json={"name": "Child Org", "slug": new_slug},
    )
    assert resp.status_code == 201
    assert resp.json()["slug"] == new_slug


@pytest.mark.asyncio
async def test_switch_tenant_issues_new_tokens(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]
    home_id = reg["tenant_id"]
    new_slug = f"switch-{uuid.uuid4().hex[:8]}"

    create = await client.post(
        "/api/v1/tenants",
        headers=_auth(token),
        json={"name": "Switch Target", "slug": new_slug},
    )
    assert create.status_code == 201
    target_id = create.json()["id"]

    switch = await client.post(
        "/api/v1/tenants/switch",
        headers=_auth(token),
        json={"tenant_id": target_id},
    )
    assert switch.status_code == 200
    new_token = switch.json()["access_token"]

    me = await client.get("/api/v1/me", headers=_auth(new_token))
    assert me.status_code == 200
    assert me.json()["tenant_id"] == target_id
    assert me.json()["tenant_id"] != home_id


@pytest.mark.asyncio
async def test_invite_member(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]
    tenant_id = reg["tenant_id"]
    invite_email = f"ops-{uuid.uuid4().hex[:6]}@example.com"

    resp = await client.post(
        f"/api/v1/tenants/{tenant_id}/members",
        headers=_auth(token),
        json={
            "email": invite_email,
            "password": PASSWORD,
            "role": "operator",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == invite_email
    assert resp.json()["role"] == "operator"
