"""Super admin console tests."""

from __future__ import annotations

import uuid

import pytest
from app.database import async_session
from app.models.super_admin_action import SuperAdminAction
from app.models.user import User
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


async def _register(client: AsyncClient, slug: str, email: str) -> dict[str, object]:
    resp = await client.post(
        "/auth/register",
        json={"email": email, "password": PASSWORD, "tenant_name": "Test Tenant", "tenant_slug": slug},
    )
    assert resp.status_code == 201
    return resp.json()


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _add_super(client: AsyncClient, tenant_id: uuid.UUID, email: str) -> str:
    async with async_session() as db:
        from app.auth.security import hash_password
        from app.models.tenant_membership import TenantMembership

        user = User(
            tenant_id=tenant_id,
            email=email,
            password_hash=hash_password(PASSWORD),
            role="super_admin",
        )
        db.add(user)
        await db.flush()
        db.add(TenantMembership(user_id=user.id, tenant_id=tenant_id, role="super_admin"))
        await db.commit()
    login = await client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200
    return str(login.json()["access_token"])


@pytest.mark.asyncio
async def test_super_admin_stats_platform_wide(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/stats", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_tenants"] >= 1


@pytest.mark.asyncio
async def test_super_admin_list_tenants_filter(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    await _register(client, unique_slug, unique_email)
    reg2 = await _register(client, f"{unique_slug}-b", f"b-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(reg2["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/tenants?status=trial", headers=_auth(token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_super_admin_suspend_tenant(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    target = await _register(client, unique_slug, unique_email)
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    tid = str(target["tenant_id"])
    resp = await client.post(f"/api/v1/super-admin/tenants/{tid}/suspend", headers=_auth(token))
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_super_admin_extend_trial(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    target = await _register(client, unique_slug, unique_email)
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    resp = await client.post(
        f"/api/v1/super-admin/tenants/{target['tenant_id']}/extend-trial",
        headers=_auth(token),
        json={"days": 7},
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_super_admin_change_plan(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    target = await _register(client, unique_slug, unique_email)
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    resp = await client.post(
        f"/api/v1/super-admin/tenants/{target['tenant_id']}/change-plan",
        headers=_auth(token),
        json={"plan_code": "pro", "prorate": True},
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_super_admin_role_required(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    resp = await client.get("/api/v1/super-admin/stats", headers=_auth(token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_super_admin_audit_log_recorded(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    target = await _register(client, unique_slug, unique_email)
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    await client.post(f"/api/v1/super-admin/tenants/{target['tenant_id']}/suspend", headers=_auth(token))
    async with async_session() as db:
        row = await db.scalar(
            select(SuperAdminAction).where(SuperAdminAction.action == "suspend_tenant").limit(1)
        )
        assert row is not None


@pytest.mark.asyncio
async def test_super_admin_impersonate_tenant_logs(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    target = await _register(client, unique_slug, unique_email)
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    resp = await client.post(
        f"/api/v1/super-admin/tenants/{target['tenant_id']}/impersonate",
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    async with async_session() as db:
        row = await db.scalar(
            select(SuperAdminAction).where(SuperAdminAction.action == "impersonate_tenant").limit(1)
        )
        assert row is not None


@pytest.mark.asyncio
async def test_revenue_mrr_calculation(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/revenue", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert "mrr_idr" in body
    assert body["arr_idr"] == body["mrr_idr"] * 12


@pytest.mark.asyncio
async def test_super_admin_tenants_list_filter_search(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    slug = f"acme-search-{unique_slug}"
    await _register(client, slug, unique_email)
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    resp = await client.get(f"/api/v1/super-admin/tenants?q={slug[:8]}", headers=_auth(token))
    assert resp.status_code == 200
    rows = resp.json()
    assert any(slug in row["slug"] for row in rows)


@pytest.mark.asyncio
async def test_super_admin_suspend_tenant_logs_audit(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    target = await _register(client, unique_slug, unique_email)
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    tid = str(target["tenant_id"])
    resp = await client.post(
        f"/api/v1/super-admin/tenants/{tid}/suspend",
        headers=_auth(token),
        json={"reason": "policy"},
    )
    assert resp.status_code == 204
    async with async_session() as db:
        row = await db.scalar(
            select(SuperAdminAction).where(SuperAdminAction.action == "suspend_tenant").limit(1)
        )
        assert row is not None


@pytest.mark.asyncio
async def test_super_admin_extend_trial_updates_trial_ends_at(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    from datetime import UTC, datetime, timedelta

    from app.models.tenant_subscription import TenantSubscription

    target = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(str(target["tenant_id"]))
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    before = datetime.now(tz=UTC)
    await client.post(
        f"/api/v1/super-admin/tenants/{tenant_id}/extend-trial",
        headers=_auth(token),
        json={"days": 10},
    )
    async with async_session() as db:
        sub = await db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id))
        assert sub is not None
        assert sub.trial_ends_at is not None
        assert sub.trial_ends_at >= before + timedelta(days=9)


@pytest.mark.asyncio
async def test_super_admin_change_plan_prorate(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    from app.models.subscription_plan import SubscriptionPlan
    from app.models.tenant_subscription import TenantSubscription

    target = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(str(target["tenant_id"]))
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    await client.post(
        f"/api/v1/super-admin/tenants/{tenant_id}/change-plan",
        headers=_auth(token),
        json={"plan_code": "pro", "prorate": True},
    )
    async with async_session() as db:
        sub = await db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id))
        assert sub is not None
        plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == sub.plan_id))
        assert plan is not None
        assert plan.code == "pro"


@pytest.mark.asyncio
async def test_system_health_check(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/system-health", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["api"] == "ok"
    assert "mqtt_subscriber" in body
    assert "checked_at" in body
