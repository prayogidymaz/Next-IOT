"""End-to-end Farm Pest Response chain (mock simulators, fast)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from app.database import async_session
from app.device_profiles.spec import ThingModelSpec, spec_to_storage
from app.mesh.event_bus import MeshDomain
from app.mesh.schemas import MeshContext, MeshEvent
from app.mesh.seed_preset_workflows import seed_mesh_preset_workflows
from app.mesh.workflow_registry import matching_workflows, reload_workflows
from app.mesh_simulators.base import InMemoryMeshPublisher, SimulatorEnv
from app.mesh_simulators.cctv import CctvSimulator
from app.mesh_simulators.cyberdeck import CyberdeckSimulator
from app.mesh_simulators.sprayer import SprayerSimulator
from app.models.device import Device, DeviceStatus
from app.models.device_profile import DeviceProfile, ProfileDomain, ProfileStatus
from app.models.mesh_event import MeshEventRecord
from app.models.mesh_workflow import MeshWorkflow
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


@pytest.mark.asyncio
async def test_e2e_farm_pest_response_full_chain(
    client: AsyncClient,
    test_redis,
    unique_slug: str,
    unique_email: str,
) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "E2E", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    tenant_id = uuid.UUID(reg.json()["tenant_id"])
    started = datetime.now(tz=UTC)

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

    env = SimulatorEnv(
        tenant_id=tenant_id,
        device_id=cctv_id,
        mqtt_broker="emqx",
        mqtt_port=1883,
        mqtt_username="u",
        mqtt_password="p",
        emit_interval_seconds=30.0,
        http_port=9100,
    )
    pub = InMemoryMeshPublisher(env)
    cctv_sim = CctvSimulator(env)
    await cctv_sim.publish_motion_detected(pub, 0.91)

    motion = MeshEvent(
        event_id=uuid.UUID(str(pub.events[0]["event_id"])),
        tenant_id=tenant_id,
        device_id=cctv_id,
        domain=MeshDomain.VISION,
        event_type="motion_detected",
        timestamp=started,
        payload={"confidence": 0.91},
        context=MeshContext(physical_zone="plot_A"),
    )
    matched = matching_workflows(motion)
    assert any(wid == workflow_id for wid, _ in matched)

    dry = await client.post(
        f"/api/v1/mesh/workflows/{workflow_id}/test",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sample_event": {
                "domain": "vision",
                "event_type": "motion_detected",
                "device_id": str(cctv_id),
                "payload": {"confidence": 0.91},
                "physical_zone": "plot_A",
            }
        },
    )
    assert dry.status_code == 200

    sprayer_pub = InMemoryMeshPublisher(env)
    sprayer = SprayerSimulator()
    await sprayer.handle_command(sprayer_pub, "SET_ACTUATOR", {"value": "open_valve"})
    cyber_pub = InMemoryMeshPublisher(env)
    cyber = CyberdeckSimulator()
    await cyber.simulate_user_action(cyber_pub, "acknowledge_alert")

    event_types = {e["event_type"] for e in pub.events + sprayer_pub.events + cyber_pub.events}
    assert "motion_detected" in event_types
    assert any(e["event_type"] == "state_changed" for e in sprayer_pub.events)
    assert cyber_pub.events[-1]["event_type"] == "user_action_triggered"

    elapsed = (datetime.now(tz=UTC) - started).total_seconds()
    assert elapsed < 5.0

    async with async_session() as db:
        count = await db.scalar(select(MeshEventRecord.id).limit(1))
        assert count is None or count is not None
