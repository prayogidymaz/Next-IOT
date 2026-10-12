"""Email template API tests."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from tests.super_admin.test_super_admin_api import _add_super, _auth, _register

CODES = [
    "welcome",
    "verify_email",
    "password_reset",
    "invoice_created",
    "invoice_paid",
]


@pytest.mark.asyncio
@pytest.mark.parametrize("code", CODES)
async def test_email_template_get_by_code(client: AsyncClient, unique_slug: str, unique_email: str, code: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    resp = await client.get(f"/api/v1/super-admin/email-templates/{code}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["code"] == code
