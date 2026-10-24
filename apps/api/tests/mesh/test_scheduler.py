"""Mesh workflow schedule runner tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from app.database import async_session
from app.mesh.scheduler import run_mesh_schedule_tick
from app.mesh.workflow_registry import reload_workflows, scheduled_workflows

PASSWORD = "SecurePass123!"


@pytest.mark.asyncio
async def test_mesh_scheduler_loads_schedule_workflows(client, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Sched", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    tenant_id = uuid.UUID(reg.json()["tenant_id"])
    token = reg.json()["tokens"]["access_token"]
    await client.post(
        "/api/v1/mesh/workflows",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Nightly scan",
            "description": "",
            "enabled": True,
            "trigger": {"type": "schedule", "filter": {"schedule_cron": "0 2 * * *"}},
            "conditions": [],
            "actions": [
                {
                    "id": "log1",
                    "type": "log_event",
                    "log_message": "scheduled tick",
                }
            ],
        },
    )
    async with async_session() as db:
        await reload_workflows(db, tenant_id)
    entries = scheduled_workflows()
    assert any(e[0] == tenant_id for e in entries)


@pytest.mark.asyncio
async def test_mesh_scheduler_fires_cron_at_right_time(
    client,
    test_redis,
    unique_slug: str,
    unique_email: str,
) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "CronFire", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    tenant_id = uuid.UUID(reg.json()["tenant_id"])
    token = reg.json()["tokens"]["access_token"]
    created = await client.post(
        "/api/v1/mesh/workflows",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Every minute",
            "enabled": True,
            "trigger": {"type": "schedule", "filter": {"schedule_cron": "* * * * *"}},
            "conditions": [],
            "actions": [{"id": "a1", "type": "log_event", "log_message": "tick"}],
        },
    )
    workflow_id = uuid.UUID(created.json()["id"])
    async with async_session() as db:
        await reload_workflows(db, tenant_id)
    now = datetime.now(tz=UTC)
    async with async_session() as db:
        checked, fired = await run_mesh_schedule_tick(db, test_redis, now)
        await db.commit()
    assert checked >= 1
    assert fired >= 1
    assert any(entry[1] == workflow_id for entry in scheduled_workflows())


@pytest.mark.asyncio
async def test_mesh_scheduler_hot_reload_on_workflow_crud(client, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Sched2", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    tenant_id = uuid.UUID(reg.json()["tenant_id"])
    token = reg.json()["tokens"]["access_token"]
    created = await client.post(
        "/api/v1/mesh/workflows",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Temp schedule",
            "enabled": True,
            "trigger": {"type": "schedule", "filter": {"schedule_cron": "5 4 * * *"}},
            "conditions": [],
            "actions": [{"id": "log1", "type": "log_event", "log_message": "x"}],
        },
    )
    workflow_id = created.json()["id"]
    async with async_session() as db:
        await reload_workflows(db, tenant_id)
    before = len([e for e in scheduled_workflows() if e[1] == uuid.UUID(workflow_id)])
    assert before == 1
    await client.delete(
        f"/api/v1/mesh/workflows/{workflow_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    async with async_session() as db:
        await reload_workflows(db, tenant_id)
    after = len([e for e in scheduled_workflows() if e[1] == uuid.UUID(workflow_id)])
    assert after == 0
