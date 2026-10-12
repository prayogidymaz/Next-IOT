"""Partner management tests."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from httpx import AsyncClient
from tests.super_admin.test_super_admin_api import _add_super, _auth, _register


@pytest.mark.asyncio
async def test_partner_update(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    created = await client.post("/api/v1/super-admin/partners", headers=_auth(token), json={"name": "P1"})
    pid = created.json()["id"]
    updated = await client.put(
        f"/api/v1/super-admin/partners/{pid}",
        headers=_auth(token),
        json={"status": "active", "tier": "platinum"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "active"


@pytest.mark.asyncio
async def test_partner_mark_commission_paid(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    partner = await client.post("/api/v1/super-admin/partners", headers=_auth(token), json={"name": "P2"})
    pid = partner.json()["id"]
    calc = await client.post(
        f"/api/v1/super-admin/partners/{pid}/commissions/calculate",
        headers=_auth(token),
        json={"period_month": date.today().replace(day=1).isoformat()},
    )
    cid = calc.json()["id"]
    paid = await client.post(
        f"/api/v1/super-admin/partners/{pid}/commissions/{cid}/mark-paid",
        headers=_auth(token),
    )
    assert paid.status_code == 200
    assert paid.json()["status"] == "paid"
