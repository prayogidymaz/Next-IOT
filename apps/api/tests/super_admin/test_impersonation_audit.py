"""Impersonation audit tests."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from tests.super_admin.test_super_admin_api import _add_super, _auth, _register


@pytest.mark.asyncio
async def test_impersonation_token_logs_api_call(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    target = await _register(client, unique_slug, unique_email)
    admin = await _register(client, f"{unique_slug}-adm", f"adm-{unique_email}")
    super_token = await _add_super(client, uuid.UUID(str(admin["tenant_id"])), f"super-{unique_email}")
    imp = await client.post(
        f"/api/v1/super-admin/tenants/{target['tenant_id']}/impersonate",
        headers=_auth(super_token),
    )
    imp_token = imp.json()["access_token"]
    sid = imp.json()["impersonation_session_id"]
    await client.get("/api/v1/me", headers=_auth(imp_token))
    actions = await client.get(
        f"/api/v1/super-admin/impersonation/sessions/{sid}/actions",
        headers=_auth(super_token),
    )
    assert actions.status_code == 200
    assert any(a["action"] == "api_call" for a in actions.json())
