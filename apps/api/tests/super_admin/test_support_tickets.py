"""Support ticket lifecycle tests."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from tests.super_admin.test_super_admin_api import _add_super, _auth, _register


@pytest.mark.asyncio
async def test_tenant_lists_own_tickets(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    await client.post(
        "/api/v1/support/tickets",
        headers=_auth(token),
        json={"subject": "A", "description": "B", "category": "other", "priority": "low"},
    )
    listed = await client.get("/api/v1/support/tickets", headers=_auth(token))
    assert listed.status_code == 200
    assert len(listed.json()) >= 1


@pytest.mark.asyncio
async def test_ticket_status_change(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    tenant_token = str(reg["tokens"]["access_token"])
    created = await client.post(
        "/api/v1/support/tickets",
        headers=_auth(tenant_token),
        json={"subject": "Close me", "description": "x", "category": "bug", "priority": "urgent"},
    )
    tid = created.json()["id"]
    super_token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.post(
        f"/api/v1/super-admin/support-tickets/{tid}/status",
        headers=_auth(super_token),
        json={"status": "resolved"},
    )
    assert resp.status_code == 204
