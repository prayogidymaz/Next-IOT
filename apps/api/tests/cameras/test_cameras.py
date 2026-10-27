"""Camera gateway tests."""

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
from app.models.device import Device, DeviceStatus
from app.models.device_profile import DeviceProfile, ProfileDomain, ProfileStatus
from app.models.mesh_event import MeshEventRecord
from app.models.mesh_workflow import MeshWorkflow
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


async def _register(client: AsyncClient, slug: str, email: str) -> tuple[str, uuid.UUID]:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Cam", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    body = reg.json()
    return body["tokens"]["access_token"], uuid.UUID(body["tenant_id"])


@pytest.mark.asyncio
async def test_camera_crud(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token, _tenant_id = await _register(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {token}"}
    create = await client.post(
        "/api/v1/cameras",
        headers=headers,
        json={
            "name": "Gate Cam",
            "rtsp_url": "rtsp://192.168.1.10/stream1",
            "username": "admin",
            "password": "secret",
            "location": "gate",
        },
    )
    assert create.status_code == 201
    cam_id = create.json()["id"]
    listed = await client.get("/api/v1/cameras", headers=headers)
    assert listed.status_code == 200
    assert any(row["id"] == cam_id for row in listed.json())


@pytest.mark.asyncio
async def test_snapshot_placeholder(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token, _ = await _register(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {token}"}
    create = await client.post(
        "/api/v1/cameras",
        headers=headers,
        json={"name": "Plot Cam", "rtsp_url": "rtsp://local/live"},
    )
    cam_id = create.json()["id"]
    snap = await client.get(f"/api/v1/cameras/{cam_id}/snapshot", headers=headers)
    assert snap.status_code == 200
    assert "placeholder-snapshot" in snap.json()["image_url"]


@pytest.mark.asyncio
async def test_ingest_motion_publishes_mesh_event(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token, tenant_id = await _register(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {token}"}
    async with async_session() as db:
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
        )
        db.add(profile)
        await db.flush()
        device = Device(
            tenant_id=tenant_id,
            profile_id=profile.id,
            name="cctv-1",
            device_type="cctv",
            status=DeviceStatus.ONLINE,
        )
        db.add(device)
        await db.commit()
        device_id = device.id

    create = await client.post(
        "/api/v1/cameras",
        headers=headers,
        json={
            "name": "CCTV",
            "rtsp_url": "rtsp://cam/live",
            "mesh_device_id": str(device_id),
            "physical_zone": "plot_A",
        },
    )
    cam_id = create.json()["id"]
    motion = await client.post(
        f"/api/v1/cameras/{cam_id}/ingest-motion",
        headers=headers,
        json={"confidence": 0.91, "bbox": [0.1, 0.2, 0.3, 0.4]},
    )
    assert motion.status_code == 200
    assert motion.json()["mesh_event_id"] is not None

    async with async_session() as db:
        row = await db.scalar(select(MeshEventRecord).where(MeshEventRecord.tenant_id == tenant_id))
        assert row is not None
        assert row.event_type == "motion_detected"
        assert row.domain == MeshDomain.VISION.value


@pytest.mark.asyncio
async def test_motion_event_triggers_pest_response_workflow(
    client: AsyncClient, unique_slug: str, unique_email: str
) -> None:
    token, tenant_id = await _register(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {token}"}
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
        device = Device(
            tenant_id=tenant_id,
            profile_id=profile.id,
            name="cctv-e2e",
            device_type="cctv",
            status=DeviceStatus.ONLINE,
        )
        db.add(device)
        await db.commit()
        device_id = device.id
        workflow = await db.scalar(
            select(MeshWorkflow).where(
                MeshWorkflow.tenant_id == tenant_id,
                MeshWorkflow.name == "Farm Pest Response",
            )
        )
        assert workflow is not None
        workflow_id = workflow.id
        await reload_workflows(db, tenant_id)

    create = await client.post(
        "/api/v1/cameras",
        headers=headers,
        json={
            "name": "CCTV E2E",
            "rtsp_url": "rtsp://cam/live",
            "mesh_device_id": str(device_id),
            "physical_zone": "plot_A",
        },
    )
    cam_id = create.json()["id"]
    motion = await client.post(
        f"/api/v1/cameras/{cam_id}/ingest-motion",
        headers=headers,
        json={"confidence": 0.91, "bbox": [0, 0, 1, 1]},
    )
    assert motion.status_code == 200
    mesh_event_id = motion.json()["mesh_event_id"]
    assert mesh_event_id is not None

    event = MeshEvent(
        event_id=uuid.UUID(mesh_event_id),
        tenant_id=tenant_id,
        device_id=device_id,
        domain=MeshDomain.VISION,
        event_type="motion_detected",
        timestamp=datetime.now(tz=UTC),
        payload={"confidence": 0.91},
        context=MeshContext(physical_zone="plot_A"),
    )
    matched = matching_workflows(event)
    assert any(wid == workflow_id for wid, _ in matched)
