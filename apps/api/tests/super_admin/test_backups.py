"""Backup API tests."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from tests.super_admin.test_super_admin_api import _add_super, _auth, _register


@pytest.mark.asyncio
async def test_backup_delete(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await _register(client, unique_slug, unique_email)
    token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    trig = await client.post(
        "/api/v1/super-admin/backups/trigger",
        headers=_auth(token),
        json={"backup_type": "database_only"},
    )
    bid = trig.json()["id"]
    deleted = await client.delete(f"/api/v1/super-admin/backups/{bid}", headers=_auth(token))
    assert deleted.status_code == 204
