"""Extended super-admin console API tests."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from tests.super_admin.test_super_admin_api import _add_super, _auth, _register


@pytest.mark.asyncio
async def test_audit_log_filter_by_date(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    target = await _register(client, unique_slug, unique_email)
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    await client.post(f"/api/v1/super-admin/tenants/{target['tenant_id']}/suspend", headers=_auth(token))
    resp = await client.get("/api/v1/super-admin/audit-log?action=suspend_tenant", headers=_auth(token))
    assert resp.status_code == 200
    rows = resp.json()
    assert any(r["action"] == "suspend_tenant" for r in rows)


@pytest.mark.asyncio
async def test_analytics_cohort_calculation(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/analytics/cohort?months=6", headers=_auth(token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_health_score_computation(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/health-scores", headers=_auth(token))
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) >= 1
    assert 0 <= rows[0]["score"] <= 100


@pytest.mark.asyncio
async def test_mqtt_monitor_proxy(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/mqtt/stats", headers=_auth(token))
    assert resp.status_code == 200
    assert "connections" in resp.json()


@pytest.mark.asyncio
async def test_rate_limit_tracking(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/rate-limits?period=24h", headers=_auth(token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_system_logs_tail(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/logs/tail?service=api&level=INFO&lines=10", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_announcement_crud(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    create = await client.post(
        "/api/v1/super-admin/announcements",
        headers=_auth(token),
        json={
            "title": "Maintenance",
            "body": "Scheduled downtime",
            "announcement_type": "warning",
            "target_filter": {"scope": "all"},
            "published": True,
        },
    )
    assert create.status_code == 201
    listed = await client.get("/api/v1/super-admin/announcements", headers=_auth(token))
    assert listed.status_code == 200
    assert any(a["title"] == "Maintenance" for a in listed.json())


@pytest.mark.asyncio
async def test_announcement_target_filter(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.post(
        "/api/v1/super-admin/announcements",
        headers=_auth(token),
        json={
            "title": "Pro only",
            "body": "Feature",
            "target_filter": {"plans": ["pro"]},
            "published": False,
        },
    )
    assert resp.status_code == 201
    assert resp.json()["target_filter"]["plans"] == ["pro"]


@pytest.mark.asyncio
async def test_promo_code_validation(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    code = f"PROMO{unique_slug[-6:].upper()}"
    created = await client.post(
        "/api/v1/super-admin/promo-codes",
        headers=_auth(token),
        json={
            "code": code,
            "discount_type": "percent",
            "discount_value": 50,
            "valid_plans": ["pro"],
            "max_uses": 10,
        },
    )
    assert created.status_code == 201
    valid = await client.get(f"/api/v1/super-admin/promo-codes/{code}/validate", headers=_auth(token))
    assert valid.status_code == 200


@pytest.mark.asyncio
async def test_platform_settings_update(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    put = await client.put(
        "/api/v1/super-admin/platform-settings",
        headers=_auth(token),
        json={"sections": {"general": {"platform_name": "Next-IoT HQ", "support_email": "ops@nextiot.com"}}},
    )
    assert put.status_code == 200
    assert put.json()["sections"]["general"]["platform_name"] == "Next-IoT HQ"


@pytest.mark.asyncio
async def test_feature_flag_toggle(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    flags = await client.get("/api/v1/super-admin/feature-flags", headers=_auth(token))
    assert flags.status_code == 200
    flag_id = flags.json()[0]["id"]
    updated = await client.put(
        f"/api/v1/super-admin/feature-flags/{flag_id}",
        headers=_auth(token),
        json={"enabled_global": True, "rollout_percent": 100},
    )
    assert updated.status_code == 200
    assert updated.json()["enabled_global"] is True


@pytest.mark.asyncio
async def test_finance_export_csv(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/finance/export?format=csv", headers=_auth(token))
    assert resp.status_code == 200
    assert "invoice_id" in resp.text


@pytest.mark.asyncio
async def test_tenant_impersonation_logs_audit(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    from app.database import async_session
    from app.models.super_admin_action import SuperAdminAction
    from sqlalchemy import select

    target = await _register(client, unique_slug, unique_email)
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    await client.post(f"/api/v1/super-admin/tenants/{target['tenant_id']}/impersonate", headers=_auth(token))
    async with async_session() as db:
        row = await db.scalar(select(SuperAdminAction).where(SuperAdminAction.action == "impersonate_tenant"))
        assert row is not None


@pytest.mark.asyncio
async def test_analytics_deep_dive(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/analytics/deep-dive", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert "arpa_idr" in body
    assert "churn_by_plan" in body


@pytest.mark.asyncio
async def test_audit_log_export_csv(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/audit-log/export", headers=_auth(token))
    assert resp.status_code == 200
    assert "timestamp" in resp.text


@pytest.mark.asyncio
async def test_stats_includes_messages_today(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/stats", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert "messages_today" in body
    assert "arr_idr" in body
