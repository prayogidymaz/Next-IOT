"""Integration coverage for agriculture analytics and calendar."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from tests.agriculture.conftest import auth, create_farm, create_plot, register_tenant
from tests.super_admin.test_super_admin_api import _add_super, _auth


@pytest.mark.asyncio
async def test_calendar_yield_analytics(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await register_tenant(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    farm = await create_farm(client, token)
    farm_id = str(farm["id"])
    plot = await create_plot(client, token, farm_id)
    cal = await client.post(
        f"/api/agriculture/farms/{farm_id}/calendar",
        headers=auth(token),
        json={"stage": "vegetative", "started_at": "2026-01-01T00:00:00Z"},
    )
    assert cal.status_code == 201
    tasks = await client.get(f"/api/agriculture/farms/{farm_id}/next-tasks", headers=auth(token))
    assert tasks.status_code == 200
    yld = await client.post(
        f"/api/agriculture/plots/{plot['id']}/yield",
        headers=auth(token),
        json={"harvest_date": "2026-06-01", "quantity_kg": "100", "price_per_kg_idr": 50000},
    )
    assert yld.status_code == 201
    ya = await client.get(f"/api/agriculture/farms/{farm_id}/yield-analytics", headers=auth(token))
    assert ya.status_code == 200
    water = await client.get(f"/api/agriculture/farms/{farm_id}/analytics/water-usage", headers=auth(token))
    assert water.status_code == 200
    env = await client.get(f"/api/agriculture/farms/{farm_id}/analytics/environmental", headers=auth(token))
    assert env.status_code == 200
    cost = await client.get(f"/api/agriculture/farms/{farm_id}/analytics/cost-vs-yield", headers=auth(token))
    assert cost.status_code == 200
    forecast = await client.get(f"/api/agriculture/farms/{farm_id}/disease-risk-forecast", headers=auth(token))
    assert forecast.status_code == 200


@pytest.mark.asyncio
async def test_super_admin_agri_stats(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await register_tenant(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    await create_farm(client, token)
    super_token = await _add_super(client, uuid.UUID(str(reg["tenant_id"])), f"super-{unique_email}")
    stats = await client.get("/api/v1/super-admin/agriculture/stats", headers=_auth(super_token))
    assert stats.status_code == 200
    assert stats.json()["total_farms"] >= 1
