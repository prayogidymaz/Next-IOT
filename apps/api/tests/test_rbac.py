import uuid

import pytest
from httpx import AsyncClient

from app.auth.security import hash_password
from app.auth.tiering import SecurityTier
from app.database import async_session
from app.models.tenant import Tenant
from app.models.user import User

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


async def _login(client: AsyncClient, email: str) -> str:
    resp = await client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 200
    return resp.json()["access_token"]


async def _add_user(
    tenant_id: uuid.UUID,
    email: str,
    role: str,
) -> User:
    async with async_session() as session:
        user = User(
            tenant_id=tenant_id,
            email=email,
            password_hash=hash_password(PASSWORD),
            role=role,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_profile(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]

    resp = await client.get("/api/v1/me", headers=_auth(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == unique_email
    assert data["role"] == "tenant_admin"
    assert data["security_tier"] == "free"
    assert data["tier_level"] == 1


@pytest.mark.asyncio
async def test_tenant_admin_can_list_users(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]

    resp = await client.get("/api/v1/admin/users", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_viewer_denied_admin_endpoint(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(reg["tenant_id"])
    viewer_email = f"viewer-{uuid.uuid4().hex[:6]}@example.com"
    await _add_user(tenant_id, viewer_email, "viewer")

    token = await _login(client, viewer_email)
    resp = await client.get("/api/v1/admin/users", headers=_auth(token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_operator_can_send_command_viewer_cannot(
    client: AsyncClient, unique_slug: str, unique_email: str
):
    reg = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(reg["tenant_id"])

    operator_email = f"op-{uuid.uuid4().hex[:6]}@example.com"
    viewer_email = f"view-{uuid.uuid4().hex[:6]}@example.com"
    await _add_user(tenant_id, operator_email, "operator")
    await _add_user(tenant_id, viewer_email, "viewer")

    op_token = await _login(client, operator_email)
    viewer_token = await _login(client, viewer_email)

    op_resp = await client.post("/api/v1/devices/command", headers=_auth(op_token))
    assert op_resp.status_code == 204

    viewer_resp = await client.post("/api/v1/devices/command", headers=_auth(viewer_token))
    assert viewer_resp.status_code == 403


@pytest.mark.asyncio
async def test_tenant_isolation_cross_tenant_denied(client: AsyncClient):
    slug_a = f"tenant-a-{uuid.uuid4().hex[:6]}"
    slug_b = f"tenant-b-{uuid.uuid4().hex[:6]}"
    email_a = f"a-{uuid.uuid4().hex[:6]}@example.com"
    email_b = f"b-{uuid.uuid4().hex[:6]}@example.com"

    reg_a = await _register(client, slug_a, email_a)
    reg_b = await _register(client, slug_b, email_b)

    token_a = reg_a["tokens"]["access_token"]
    tenant_b_id = reg_b["tenant_id"]

    resp = await client.get(f"/api/v1/tenants/{tenant_b_id}", headers=_auth(token_a))
    assert resp.status_code == 403
    assert "tenant isolation" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_super_admin_cross_tenant_and_super_endpoint(client: AsyncClient):
    slug_a = f"tenant-a-{uuid.uuid4().hex[:6]}"
    slug_b = f"tenant-b-{uuid.uuid4().hex[:6]}"
    email_a = f"a-{uuid.uuid4().hex[:6]}@example.com"
    email_b = f"b-{uuid.uuid4().hex[:6]}@example.com"

    reg_a = await _register(client, slug_a, email_a)
    reg_b = await _register(client, slug_b, email_b)
    tenant_b_id = reg_b["tenant_id"]

    super_email = f"super-{uuid.uuid4().hex[:6]}@example.com"
    await _add_user(uuid.UUID(reg_a["tenant_id"]), super_email, "super_admin")
    super_token = await _login(client, super_email)

    cross = await client.get(f"/api/v1/tenants/{tenant_b_id}", headers=_auth(super_token))
    assert cross.status_code == 200

    super_list = await client.get("/api/v1/super/tenants", headers=_auth(super_token))
    assert super_list.status_code == 200
    assert len(super_list.json()) >= 2

    tenant_admin_token = reg_a["tokens"]["access_token"]
    denied = await client.get("/api/v1/super/tenants", headers=_auth(tenant_admin_token))
    assert denied.status_code == 403


@pytest.mark.asyncio
async def test_rate_limit_per_tier(client: AsyncClient, unique_slug: str, unique_email: str):
    import app.auth.tiering as tiering_module

    original = tiering_module.TIER_RATE_LIMITS[SecurityTier.FREE]
    tiering_module.TIER_RATE_LIMITS[SecurityTier.FREE] = 3

    try:
        reg = await _register(client, unique_slug, unique_email)
        token = reg["tokens"]["access_token"]
        headers = _auth(token)

        for _ in range(3):
            resp = await client.get("/api/v1/me", headers=headers)
            assert resp.status_code == 200

        resp = await client.get("/api/v1/me", headers=headers)
        assert resp.status_code == 429
    finally:
        tiering_module.TIER_RATE_LIMITS[SecurityTier.FREE] = original
