"""Workflow analytics tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from app.types.json_types import JsonObject
from app.workflows.analytics.service import _estimate_savings_from_definition


def test_estimate_savings_valve_action() -> None:
    definition: JsonObject = {
        "actions": [{"type": "set_actuator", "duration_minutes": 15}],
    }
    water, kwh, idr = _estimate_savings_from_definition(definition)
    assert water == 37.0
    assert idr > 0


def test_estimate_savings_empty() -> None:
    water, kwh, idr = _estimate_savings_from_definition({})
    assert water == 0.0
    assert kwh == 0.0


def test_estimate_lighting_kwh() -> None:
    definition: JsonObject = {
        "actions": [{"type": "set_actuator", "duration_minutes": 60, "channels": "lighting"}],
    }
    _, kwh, _ = _estimate_savings_from_definition(definition)
    assert kwh >= 0.5


@pytest.mark.asyncio
async def test_top_fired_empty_tenant() -> None:
    from app.database import async_session
    from app.models.tenant import Tenant
    from app.workflows.analytics.service import WorkflowAnalyticsService

    async with async_session() as db:
        tenant = Tenant(name="Top", slug=f"top-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        stats = await WorkflowAnalyticsService(db).top_fired_workflows(tenant.id, 30, 10)
        assert stats == []


@pytest.mark.asyncio
async def test_timeline_empty() -> None:
    from app.auth.context import CurrentUser
    from app.auth.tiering import SecurityTier
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.models.tenant import Tenant
    from app.workflows.analytics.service import WorkflowAnalyticsService

    async with async_session() as db:
        tenant = Tenant(name="Tl", slug=f"tl-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        mesh = MeshWorkflow(tenant_id=tenant.id, name="W", description="", enabled=False, definition={})
        db.add(mesh)
        await db.flush()
        user = CurrentUser(
            user_id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="t@example.com",
            role="tenant_admin",
            security_tier=SecurityTier.PRO,
        )
        data = await WorkflowAnalyticsService(db).workflow_timeline(mesh.id, user, 7)
        assert data.points == []


@pytest.mark.asyncio
async def test_savings_report() -> None:
    from app.auth.context import CurrentUser
    from app.auth.tiering import SecurityTier
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.models.tenant import Tenant
    from app.workflows.analytics.service import WorkflowAnalyticsService

    async with async_session() as db:
        tenant = Tenant(name="Sv", slug=f"sv-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        mesh = MeshWorkflow(
            tenant_id=tenant.id,
            name="W",
            description="",
            enabled=False,
            definition={"actions": [{"type": "set_actuator", "duration_minutes": 15}]},
        )
        db.add(mesh)
        await db.flush()
        user = CurrentUser(
            user_id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="s@example.com",
            role="tenant_admin",
            security_tier=SecurityTier.PRO,
        )
        report = await WorkflowAnalyticsService(db).savings_per_workflow(mesh.id, user)
        assert report.water_liters_saved == 0.0


@pytest.mark.asyncio
async def test_failure_analysis_no_executions() -> None:
    from app.auth.context import CurrentUser
    from app.auth.tiering import SecurityTier
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.models.tenant import Tenant
    from app.workflows.analytics.service import WorkflowAnalyticsService

    async with async_session() as db:
        tenant = Tenant(name="Fl", slug=f"fl-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        mesh = MeshWorkflow(tenant_id=tenant.id, name="W", description="", enabled=False, definition={})
        db.add(mesh)
        await db.flush()
        user = CurrentUser(
            user_id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="f@example.com",
            role="tenant_admin",
            security_tier=SecurityTier.PRO,
        )
        report = await WorkflowAnalyticsService(db).failure_analysis(mesh.id, user)
        assert report.failure_rate == 0.0


@pytest.mark.asyncio
async def test_failure_analysis_with_failed_run() -> None:
    from app.auth.context import CurrentUser
    from app.auth.tiering import SecurityTier
    from app.database import async_session
    from app.mesh.workflow_schema import WorkflowExecutionStatus
    from app.models.mesh_workflow import MeshWorkflow, MeshWorkflowExecution
    from app.models.tenant import Tenant
    from app.workflows.analytics.service import WorkflowAnalyticsService

    async with async_session() as db:
        tenant = Tenant(name="Ff", slug=f"ff-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        mesh = MeshWorkflow(tenant_id=tenant.id, name="W", description="", enabled=False, definition={})
        db.add(mesh)
        await db.flush()
        db.add(
            MeshWorkflowExecution(
                tenant_id=tenant.id,
                workflow_id=mesh.id,
                status=WorkflowExecutionStatus.FAILED.value,
                started_at=datetime.now(tz=UTC),
                action_results={"step1": {"ok": False}},
                error_message="device offline",
            )
        )
        await db.flush()
        user = CurrentUser(
            user_id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="f2@example.com",
            role="tenant_admin",
            security_tier=SecurityTier.PRO,
        )
        report = await WorkflowAnalyticsService(db).failure_analysis(mesh.id, user)
        assert report.failure_rate == 1.0
        assert "device offline" in report.common_errors
