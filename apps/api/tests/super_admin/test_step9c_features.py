"""Step 9C super-admin feature tests."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from httpx import AsyncClient
from tests.super_admin.test_super_admin_api import _add_super, _auth, _register


@pytest.mark.asyncio
async def test_email_templates_list(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get("/api/v1/super-admin/email-templates", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 10


@pytest.mark.asyncio
async def test_email_template_update_and_preview(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    put = await client.put(
        "/api/v1/super-admin/email-templates/welcome",
        headers=_auth(token),
        json={"subject": "Halo {{ user_name }}"},
    )
    assert put.status_code == 200
    prev = await client.post(
        "/api/v1/super-admin/email-templates/welcome/preview",
        headers=_auth(token),
        json={"sample_variables": {"user_name": "Budi", "platform_name": "Next-IoT"}},
    )
    assert prev.status_code == 200
    assert "Budi" in prev.json()["subject"]


@pytest.mark.asyncio
async def test_email_template_test_send(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.post(
        "/api/v1/super-admin/email-templates/welcome/test",
        headers=_auth(token),
        json={
            "recipient_email": "test@example.com",
            "sample_variables": {"user_name": "A", "platform_name": "Next-IoT"},
        },
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_support_ticket_tenant_create_and_admin_list(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    reg = await _register(client, unique_slug, unique_email)
    tenant_token = str(reg["tokens"]["access_token"])
    created = await client.post(
        "/api/v1/support/tickets",
        headers=_auth(tenant_token),
        json={"subject": "Help", "description": "Need assist", "category": "technical", "priority": "high"},
    )
    assert created.status_code == 201
    super_token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    listed = await client.get("/api/v1/super-admin/support-tickets", headers=_auth(super_token))
    assert listed.status_code == 200
    assert any(t["subject"] == "Help" for t in listed.json())


@pytest.mark.asyncio
async def test_support_ticket_assign_and_message(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    tenant_token = str(reg["tokens"]["access_token"])
    created = await client.post(
        "/api/v1/support/tickets",
        headers=_auth(tenant_token),
        json={"subject": "Billing", "description": "Invoice", "category": "billing", "priority": "normal"},
    )
    tid = created.json()["id"]
    super_token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    me = await client.get("/api/v1/me", headers=_auth(super_token))
    admin_id = me.json()["user_id"]
    assign = await client.post(
        f"/api/v1/super-admin/support-tickets/{tid}/assign",
        headers=_auth(super_token),
        json={"user_id": admin_id},
    )
    assert assign.status_code == 204
    msg = await client.post(
        f"/api/v1/super-admin/support-tickets/{tid}/messages",
        headers=_auth(super_token),
        json={"body": "We are checking", "is_internal": False},
    )
    assert msg.status_code == 200


@pytest.mark.asyncio
async def test_support_ticket_status_and_stats(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    stats = await client.get("/api/v1/super-admin/support-tickets/stats", headers=_auth(token))
    assert stats.status_code == 200
    assert "open" in stats.json()


@pytest.mark.asyncio
async def test_partner_crud_and_referral_code(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    created = await client.post(
        "/api/v1/super-admin/partners",
        headers=_auth(token),
        json={"name": "Acme Reseller", "contact_email": "p@acme.com", "tier": "gold", "commission_percent": 15},
    )
    assert created.status_code == 201
    assert created.json()["referral_code"].startswith("NEXT-")


@pytest.mark.asyncio
async def test_partner_commission_calculate(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    partner = await client.post(
        "/api/v1/super-admin/partners",
        headers=_auth(token),
        json={"name": "Comm Partner"},
    )
    pid = partner.json()["id"]
    calc = await client.post(
        f"/api/v1/super-admin/partners/{pid}/commissions/calculate",
        headers=_auth(token),
        json={"period_month": date.today().replace(day=1).isoformat()},
    )
    assert calc.status_code == 200


@pytest.mark.asyncio
async def test_backup_trigger_list_restore_safety(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    trig = await client.post(
        "/api/v1/super-admin/backups/trigger",
        headers=_auth(token),
        json={"backup_type": "full"},
    )
    assert trig.status_code == 201
    bid = trig.json()["id"]
    listed = await client.get("/api/v1/super-admin/backups", headers=_auth(token))
    assert listed.status_code == 200
    bad = await client.post(
        f"/api/v1/super-admin/backups/{bid}/restore",
        headers=_auth(token),
        json={"confirm_token": "wrong"},
    )
    assert bad.status_code == 400
    good = await client.post(
        f"/api/v1/super-admin/backups/{bid}/restore",
        headers=_auth(token),
        json={"confirm_token": str(bid).replace("-", "")[:8]},
    )
    assert good.status_code == 200


@pytest.mark.asyncio
async def test_impersonation_session_list(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    target = await _register(client, unique_slug, unique_email)
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    imp = await client.post(
        f"/api/v1/super-admin/tenants/{target['tenant_id']}/impersonate",
        headers=_auth(token),
    )
    assert imp.status_code == 200
    assert "impersonation_session_id" in imp.json()
    sessions = await client.get("/api/v1/super-admin/impersonation/sessions", headers=_auth(token))
    assert sessions.status_code == 200
    sid = imp.json()["impersonation_session_id"]
    actions = await client.get(f"/api/v1/super-admin/impersonation/sessions/{sid}/actions", headers=_auth(token))
    assert actions.status_code == 200
    assert len(actions.json()) >= 1
