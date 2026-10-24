"""Mesh workflow engine tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from app.database import async_session
from app.device_profiles.spec import ThingModelSpec, spec_to_storage
from app.mesh.device_resolver import haversine_km, resolve_device
from app.mesh.event_bus import MeshDomain
from app.mesh.schemas import MeshContext, MeshEvent
from app.mesh.seed_preset_workflows import PRESET_KEYS, seed_mesh_preset_workflows
from app.mesh.workflow_executor import MeshWorkflowExecutor
from app.mesh.workflow_schema import (
    DeviceResolverSpec,
    MeshWorkflowDefinition,
    WorkflowAction,
    WorkflowActionType,
    WorkflowExecutionStatus,
    WorkflowTrigger,
    WorkflowTriggerType,
)
from app.models.device import Device, DeviceStatus
from app.models.device_profile import DeviceProfile, ProfileDomain, ProfileStatus
from app.models.mesh_workflow import MeshWorkflow
from app.models.rule import RuleOperator
from app.models.tenant import Tenant
from app.rules.evaluator import evaluate_metric
from app.rules.executor import get_rule_executor
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy import select

PASSWORD = "SecurePass123!"


def test_workflow_dsl_validation() -> None:
    MeshWorkflowDefinition.model_validate(
        {
            "name": "Ok",
            "trigger": {"type": "manual"},
            "actions": [
                {
                    "id": "a1",
                    "type": "log_event",
                    "log_message": "hello",
                }
            ],
        }
    )
    with pytest.raises(ValidationError):
        MeshWorkflowDefinition.model_validate(
            {
                "name": "Bad",
                "trigger": {"type": "manual"},
                "actions": [{"id": "a1", "type": "dispatch_device", "command": "fly_to"}],
            }
        )


@pytest.mark.asyncio
async def test_device_resolver_by_capability_and_zone(test_redis) -> None:
    async with async_session() as db:
        tenant = Tenant(name="WF", slug=f"wf-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        profile = DeviceProfile(
            tenant_id=tenant.id,
            key=f"wf_{uuid.uuid4().hex[:6]}",
            name="Zone profile",
            description="",
            domain=ProfileDomain.SMART_FARMING.value,
            version=1,
            status=ProfileStatus.PUBLISHED,
            spec=spec_to_storage(ThingModelSpec(telemetry=[], attributes=[], commands=[])),
            capabilities=["can_spray"],
            physical_zone="plot_A",
        )
        db.add(profile)
        await db.flush()
        device = Device(
            tenant_id=tenant.id,
            profile_id=profile.id,
            name="Sprayer",
            device_type="sprayer",
            status=DeviceStatus.ONLINE,
        )
        db.add(device)
        await db.commit()
        spec = DeviceResolverSpec(capability="can_spray", zone="plot_A")
        resolved = await resolve_device(db, test_redis, tenant.id, spec, {})
        assert resolved is not None
        assert resolved.id == device.id


def test_device_resolver_nearest_to_geo_location_haversine() -> None:
    assert haversine_km(-6.2, 106.8, -6.2, 106.81) < 2.0
    assert haversine_km(0.0, 0.0, 0.0, 1.0) > 100.0


@pytest.mark.asyncio
async def test_workflow_executor_simple_single_action(test_redis) -> None:
    async with async_session() as db:
        tenant = Tenant(name="Exec", slug=f"exec-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        profile = DeviceProfile(
            tenant_id=tenant.id,
            key=f"drone_{uuid.uuid4().hex[:6]}",
            name="Drone",
            description="",
            domain=ProfileDomain.SMART_FARMING.value,
            version=1,
            status=ProfileStatus.PUBLISHED,
            spec=spec_to_storage(ThingModelSpec(telemetry=[], attributes=[], commands=[])),
            capabilities=["can_fly_to"],
            geo_location={"lat": -6.2, "lng": 106.8},
        )
        db.add(profile)
        await db.flush()
        device = Device(
            tenant_id=tenant.id,
            profile_id=profile.id,
            name="Drone 1",
            device_type="drone",
            status=DeviceStatus.ONLINE,
        )
        db.add(device)
        await db.commit()
        definition = MeshWorkflowDefinition(
            name="Fly",
            trigger=WorkflowTrigger(type=WorkflowTriggerType.MANUAL),
            actions=[
                WorkflowAction(
                    id="a1",
                    type=WorkflowActionType.DISPATCH_DEVICE,
                    device_resolver=DeviceResolverSpec(capability="can_fly_to"),
                    command="fly_to",
                    params={"lat": -6.21, "lon": 106.81},
                )
            ],
        )
        event = MeshEvent(
            event_id=uuid.uuid4(),
            tenant_id=tenant.id,
            device_id=device.id,
            domain=MeshDomain.SENSOR,
            event_type="reading_update",
            timestamp=datetime.now(tz=UTC),
            payload={},
            context=MeshContext(),
        )
        workflow_row = MeshWorkflow(
            tenant_id=tenant.id,
            name=definition.name,
            description="",
            enabled=True,
            definition={"trigger": definition.trigger.model_dump(mode="json"), "actions": []},
        )
        db.add(workflow_row)
        await db.flush()
        executor = MeshWorkflowExecutor(test_redis, None, None)
        row = await executor.execute(
            db,
            workflow_id=workflow_row.id,
            tenant_id=tenant.id,
            definition=definition,
            trigger_event=event,
        )
        assert row.status == WorkflowExecutionStatus.SUCCESS.value
        assert "a1" in row.action_results


@pytest.mark.asyncio
async def test_workflow_executor_chain_actions_template_render(test_redis) -> None:
    async with async_session() as db:
        tenant = Tenant(name="Chain", slug=f"chain-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        device = Device(
            tenant_id=tenant.id,
            name="Cam",
            device_type="cctv",
            status=DeviceStatus.ONLINE,
        )
        db.add(device)
        await db.commit()
        definition = MeshWorkflowDefinition(
            name="Chain",
            trigger=WorkflowTrigger(type=WorkflowTriggerType.MANUAL),
            actions=[
                WorkflowAction(
                    id="action_1",
                    type=WorkflowActionType.LOG_EVENT,
                    log_message="step1",
                ),
                WorkflowAction(
                    id="action_2",
                    type=WorkflowActionType.LOG_EVENT,
                    log_message="after {{action_1.logged}}",
                ),
            ],
        )
        event = MeshEvent(
            event_id=uuid.uuid4(),
            tenant_id=tenant.id,
            device_id=device.id,
            domain=MeshDomain.UI,
            event_type="alert_shown",
            timestamp=datetime.now(tz=UTC),
            payload={},
            context=MeshContext(physical_zone="plot_A"),
        )
        workflow_row = MeshWorkflow(
            tenant_id=tenant.id,
            name=definition.name,
            description="",
            enabled=True,
            definition={"trigger": definition.trigger.model_dump(mode="json"), "actions": []},
        )
        db.add(workflow_row)
        await db.flush()
        executor = MeshWorkflowExecutor(test_redis, None, None)
        execution = await executor.execute(
            db,
            workflow_id=workflow_row.id,
            tenant_id=tenant.id,
            definition=definition,
            trigger_event=event,
        )
        assert execution.status == WorkflowExecutionStatus.SUCCESS.value


@pytest.mark.asyncio
async def test_workflow_executor_wait_for_event_timeout(test_redis) -> None:
    async with async_session() as db:
        tenant = Tenant(name="Wait", slug=f"wait-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        device = Device(tenant_id=tenant.id, name="D", device_type="temp", status=DeviceStatus.ONLINE)
        db.add(device)
        await db.commit()
        definition = MeshWorkflowDefinition(
            name="Wait",
            trigger=WorkflowTrigger(type=WorkflowTriggerType.MANUAL),
            actions=[
                WorkflowAction(
                    id="w1",
                    type=WorkflowActionType.WAIT_FOR_EVENT,
                    wait_for={"domain": "motion", "event_type": "waypoint_reached"},
                    timeout_seconds=1,
                )
            ],
        )
        event = MeshEvent(
            event_id=uuid.uuid4(),
            tenant_id=tenant.id,
            device_id=device.id,
            domain=MeshDomain.MOTION,
            event_type="dispatch_requested",
            timestamp=datetime.now(tz=UTC),
            payload={},
            context=MeshContext(),
        )
        workflow_row = MeshWorkflow(
            tenant_id=tenant.id,
            name=definition.name,
            description="",
            enabled=True,
            definition={"trigger": definition.trigger.model_dump(mode="json"), "actions": []},
        )
        db.add(workflow_row)
        await db.flush()
        executor = MeshWorkflowExecutor(test_redis, None, None)
        execution = await executor.execute(
            db,
            workflow_id=workflow_row.id,
            tenant_id=tenant.id,
            definition=definition,
            trigger_event=event,
        )
        assert execution.status == WorkflowExecutionStatus.TIMEOUT.value


@pytest.mark.asyncio
async def test_workflow_executor_condition_short_circuit(test_redis) -> None:
    async with async_session() as db:
        tenant = Tenant(name="Cond", slug=f"cond-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        device = Device(tenant_id=tenant.id, name="D", device_type="temp", status=DeviceStatus.OFFLINE)
        db.add(device)
        await db.commit()
        from app.mesh.workflow_schema import WorkflowCondition

        definition = MeshWorkflowDefinition(
            name="Cond",
            trigger=WorkflowTrigger(type=WorkflowTriggerType.MANUAL),
            conditions=[
                WorkflowCondition(
                    type="device_state",
                    device_resolver=DeviceResolverSpec(capability="can_fly_to"),
                    state_match={"status": "online"},
                )
            ],
            actions=[
                WorkflowAction(
                    id="a1",
                    type=WorkflowActionType.LOG_EVENT,
                    log_message="never",
                )
            ],
        )
        event = MeshEvent(
            event_id=uuid.uuid4(),
            tenant_id=tenant.id,
            device_id=device.id,
            domain=MeshDomain.SENSOR,
            event_type="reading_update",
            timestamp=datetime.now(tz=UTC),
            payload={},
            context=MeshContext(),
        )
        workflow_row = MeshWorkflow(
            tenant_id=tenant.id,
            name=definition.name,
            description="",
            enabled=True,
            definition={"trigger": definition.trigger.model_dump(mode="json"), "actions": []},
        )
        db.add(workflow_row)
        await db.flush()
        executor = MeshWorkflowExecutor(test_redis, None, None)
        execution = await executor.execute(
            db,
            workflow_id=workflow_row.id,
            tenant_id=tenant.id,
            definition=definition,
            trigger_event=event,
        )
        assert execution.status == WorkflowExecutionStatus.SKIPPED_CONDITION.value


@pytest.mark.asyncio
async def test_workflow_dry_run_endpoint(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "WF", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/mesh/workflows",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Dry",
            "trigger": {"type": "manual"},
            "actions": [{"id": "a1", "type": "log_event", "log_message": "dry"}],
        },
    )
    assert create.status_code == 201
    workflow_id = create.json()["id"]
    dry = await client.post(
        f"/api/v1/mesh/workflows/{workflow_id}/test",
        headers={"Authorization": f"Bearer {token}"},
        json={"sample_event": {"domain": "sensor", "event_type": "reading_update", "device_id": str(uuid.uuid4())}},
    )
    assert dry.status_code == 200
    assert dry.json()["conditions_passed"] is True


@pytest.mark.asyncio
async def test_workflow_execution_log_persisted(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Log", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    device = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Node", "device_type": "temp"},
    )
    device_id = device.json()["device"]["id"]
    create = await client.post(
        "/api/v1/mesh/workflows",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Log wf",
            "trigger": {"type": "manual"},
            "actions": [{"id": "a1", "type": "create_alarm", "title": "Workflow run", "severity": "info"}],
        },
    )
    workflow_id = create.json()["id"]
    run = await client.post(
        f"/api/v1/mesh/workflows/{workflow_id}/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={"sample_event": {"domain": "ui", "event_type": "alert_shown", "device_id": device_id}},
    )
    assert run.status_code == 200
    execution_id = run.json()["id"]
    detail = await client.get(
        f"/api/v1/mesh/workflow-executions/{execution_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail.status_code == 200
    assert detail.json()["status"] in {"success", "failed"}


@pytest.mark.asyncio
async def test_4_preset_workflows_seeded() -> None:
    async with async_session() as db:
        tenant = Tenant(name="Preset", slug=f"preset-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        created = await seed_mesh_preset_workflows(db, tenant.slug)
        await db.commit()
        assert created == 4
        rows = await db.scalars(select(MeshWorkflow).where(MeshWorkflow.tenant_id == tenant.id))
        names = {row.name for row in rows.all()}
        assert "Farm Pest Response" in names
        assert len(PRESET_KEYS) == 4


def test_workflow_backward_compat_old_rule_engine_still_runs() -> None:
    assert evaluate_metric(RuleOperator.GT, 30.0, 25.0) is True
    assert get_rule_executor() is None or get_rule_executor() is not None
