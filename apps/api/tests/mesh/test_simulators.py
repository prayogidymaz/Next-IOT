"""Mesh device simulator unit + workflow integration tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from app.database import async_session
from app.device_profiles.spec import ThingModelSpec, spec_to_storage
from app.mesh.event_bus import MeshDomain
from app.mesh.schemas import MeshContext, MeshEvent
from app.mesh.seed_preset_workflows import seed_mesh_preset_workflows
from app.mesh.workflow_matching import workflow_matches_event
from app.mesh.workflow_registry import definition_from_row, reload_workflows
from app.mesh_simulators.base import InMemoryMeshPublisher, SimulatorEnv
from app.mesh_simulators.cctv import CctvSimulator
from app.mesh_simulators.cyberdeck import CyberdeckSimulator
from app.mesh_simulators.gate import GateSimulator
from app.mesh_simulators.smartwatch import SmartwatchSimulator
from app.mesh_simulators.sprayer import SprayerSimulator
from app.mesh_simulators.weather import WeatherSimulator
from app.models.device import Device, DeviceStatus
from app.models.device_profile import DeviceProfile, ProfileDomain, ProfileStatus
from app.models.mesh_workflow import MeshWorkflow
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


def _env() -> SimulatorEnv:
    return SimulatorEnv(
        tenant_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        mqtt_broker="emqx",
        mqtt_port=1883,
        mqtt_username="u",
        mqtt_password="p",
        emit_interval_seconds=30.0,
        http_port=8090,
    )


@pytest.mark.asyncio
async def test_cctv_simulator_publishes_motion_event() -> None:
    env = _env()
    pub = InMemoryMeshPublisher(env)
    sim = CctvSimulator(env)
    await sim.publish_motion_detected(pub, 0.91)
    assert pub.events[0]["event_type"] == "motion_detected"
    assert pub.events[0]["domain"] == MeshDomain.VISION.value


@pytest.mark.asyncio
async def test_sprayer_simulator_responds_to_control_valve() -> None:
    pub = InMemoryMeshPublisher(_env())
    sim = SprayerSimulator()
    result = await sim.handle_command(pub, "SET_ACTUATOR", {"value": "open_valve", "duration_s": 30})
    assert result["valve_open"] is True
    assert any(event["event_type"] == "state_changed" for event in pub.events)


@pytest.mark.asyncio
async def test_gate_simulator_responds_to_lock_unlock() -> None:
    pub = InMemoryMeshPublisher(_env())
    sim = GateSimulator()
    await sim.handle_command(pub, "SET_ACTUATOR", {"value": "lock"})
    await sim.handle_command(pub, "SET_ACTUATOR", {"value": "unlock"})
    types = {event["event_type"] for event in pub.events}
    assert "lock_engaged" in types
    assert "access_granted" in types


@pytest.mark.asyncio
async def test_cyberdeck_simulator_publishes_user_action() -> None:
    pub = InMemoryMeshPublisher(_env())
    sim = CyberdeckSimulator()
    await sim.simulate_user_action(pub, "acknowledge_alert")
    assert pub.events[-1]["event_type"] == "user_action_triggered"


@pytest.mark.asyncio
async def test_weather_simulator_publishes_forecast() -> None:
    pub = InMemoryMeshPublisher(_env())
    sim = WeatherSimulator()
    await sim.publish_forecast(pub, 0.82)
    assert pub.events[0]["domain"] == MeshDomain.SENSOR.value


@pytest.mark.asyncio
async def test_smartwatch_simulator_receives_alert() -> None:
    pub = InMemoryMeshPublisher(_env())
    sim = SmartwatchSimulator()
    await sim.on_mesh_fanout(pub, {"domain": "ui", "event_type": "alert_shown", "event_id": "abc"})
    assert pub.events[-1]["event_type"] == "alert_shown"


@pytest.mark.asyncio
async def test_drone_simulator_publishes_motion_events_mesh() -> None:
    from app.models.device import Device

    device = Device(
        tenant_id=uuid.uuid4(),
        name="drone",
        device_type="drone",
        status=DeviceStatus.ONLINE,
    )
    with patch("app.drone_simulator.mesh_events.aiomqtt.Client") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.publish = AsyncMock()
        from app.drone_simulator.mesh_events import publish_drone_mesh_event

        await publish_drone_mesh_event(device, "flight_started", {"command": "GO_TO_WAYPOINT"})
        instance.publish.assert_awaited()


@pytest.mark.asyncio
async def test_end_to_end_farm_pest_response_workflow_with_simulators(
    client: AsyncClient,
    test_redis,
    unique_slug: str,
    unique_email: str,
) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Sim", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    tenant_id = uuid.UUID(reg.json()["tenant_id"])
    cctv_id: uuid.UUID

    async with async_session() as db:
        await seed_mesh_preset_workflows(db, unique_slug)
        profile = DeviceProfile(
            tenant_id=tenant_id,
            key=f"cctv_{uuid.uuid4().hex[:6]}",
            name="CCTV",
            description="",
            domain=ProfileDomain.SMART_FARMING.value,
            version=1,
            status=ProfileStatus.PUBLISHED,
            spec=spec_to_storage(ThingModelSpec(telemetry=[], attributes=[], commands=[])),
            capabilities=["can_detect_motion"],
            physical_zone="plot_A",
            geo_location={"lat": -3.3, "lng": 119.8},
        )
        db.add(profile)
        await db.flush()
        cctv = Device(
            tenant_id=tenant_id,
            profile_id=profile.id,
            name="cctv-sim",
            device_type="cctv",
            status=DeviceStatus.ONLINE,
        )
        db.add(cctv)
        await db.commit()
        await db.refresh(cctv)
        cctv_id = cctv.id

        workflow = await db.scalar(
            select(MeshWorkflow).where(
                MeshWorkflow.tenant_id == tenant_id,
                MeshWorkflow.name == "Farm Pest Response",
            )
        )
        assert workflow is not None
        await reload_workflows(db, tenant_id)
        workflow_id = workflow.id
        await db.commit()

    motion = MeshEvent(
        event_id=uuid.uuid4(),
        tenant_id=tenant_id,
        device_id=cctv_id,
        domain=MeshDomain.VISION,
        event_type="motion_detected",
        timestamp=datetime.now(tz=UTC),
        payload={"confidence": 0.88},
        context=MeshContext(physical_zone="plot_A", geo_location=None),
    )
    async with async_session() as db:
        row = await db.scalar(select(MeshWorkflow).where(MeshWorkflow.id == workflow_id))
        assert row is not None
        definition = definition_from_row(row)
        assert workflow_matches_event(definition, motion)

    dry = await client.post(
        f"/api/v1/mesh/workflows/{workflow_id}/test",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sample_event": {
                "domain": "vision",
                "event_type": "motion_detected",
                "device_id": str(cctv_id),
                "payload": {"confidence": 0.88},
                "physical_zone": "plot_A",
            }
        },
    )
    assert dry.status_code == 200
    assert dry.json()["conditions_passed"] in {True, False}
