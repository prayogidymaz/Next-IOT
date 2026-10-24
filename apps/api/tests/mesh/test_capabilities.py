"""Universal Mesh capability registry tests."""

from __future__ import annotations

import uuid

import pytest
from app.database import async_session
from app.device_profiles.seed_mesh_agri import ensure_mesh_agri_device_profiles
from app.device_profiles.spec import ThingModelSpec, spec_to_storage
from app.mesh.capabilities import (
    CAPABILITY_KEYS,
    device_capabilities,
    devices_with_capability,
    infer_capabilities_from_device_type,
    infer_capabilities_from_profile,
    validate_capability,
)
from app.models.device import Device, DeviceStatus
from app.models.device_profile import DeviceProfile, ProfileDomain, ProfileStatus
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


def test_capability_key_validation() -> None:
    assert validate_capability("can_read_moisture") is True
    assert validate_capability("not_a_real_capability") is False
    assert "can_fly_to" in CAPABILITY_KEYS


def test_infer_capabilities_from_legacy_device_type() -> None:
    caps = infer_capabilities_from_device_type("lora_sensor")
    assert "can_read_moisture" in caps
    assert infer_capabilities_from_device_type("unknown_widget") == []


@pytest.mark.asyncio
async def test_devices_with_capability_query(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": "Mesh Tenant",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    assert reg.status_code == 201
    tenant_id = uuid.UUID(str(reg.json()["tenant_id"]))

    async with async_session() as db:
        profile = DeviceProfile(
            tenant_id=tenant_id,
            key=f"mesh_test_{uuid.uuid4().hex[:6]}",
            name="Mesh test profile",
            description="",
            domain=ProfileDomain.SMART_FARMING.value,
            version=1,
            status=ProfileStatus.PUBLISHED,
            spec=spec_to_storage(ThingModelSpec(telemetry=[], attributes=[], commands=[])),
            capabilities=["can_spray"],
        )
        db.add(profile)
        await db.flush()
        device = Device(
            tenant_id=tenant_id,
            profile_id=profile.id,
            name="Sprayer 1",
            device_type="sprayer",
            status=DeviceStatus.PROVISIONED,
        )
        db.add(device)
        await db.commit()
        await db.refresh(device)

        matched = await devices_with_capability(db, tenant_id, "can_spray")
        assert any(row.id == device.id for row in matched)
        assert await devices_with_capability(db, tenant_id, "invalid_cap") == []


@pytest.mark.asyncio
async def test_seed_7_mesh_agri_profiles() -> None:
    expected = {
        "agri_sensor_v2",
        "agri_cctv_outdoor",
        "agri_drone_patrol",
        "agri_sprayer_station",
        "agri_cyberdeck_field",
        "agri_gate_lock",
        "agri_weather_station",
    }
    async with async_session() as db:
        from app.config import settings
        from app.models.tenant import Tenant

        tenant = await db.scalar(select(Tenant).where(Tenant.slug == settings.seed_tenant_slug))
        if tenant is None:
            tenant = Tenant(name="Mesh seed tenant", slug=settings.seed_tenant_slug)
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)

        await ensure_mesh_agri_device_profiles(db)
        keys = await db.scalars(
            select(DeviceProfile.key).where(
                DeviceProfile.tenant_id == tenant.id,
                DeviceProfile.key.in_(sorted(expected)),
            )
        )
        assert set(keys.all()) == expected


@pytest.mark.asyncio
async def test_backward_compat_device_without_capabilities() -> None:
    profile = DeviceProfile(
        tenant_id=uuid.uuid4(),
        key="env_sensor",
        name="Legacy env",
        description="",
        domain=ProfileDomain.GENERIC.value,
        version=1,
        status=ProfileStatus.PUBLISHED,
        spec=spec_to_storage(ThingModelSpec(telemetry=[], attributes=[], commands=[])),
        capabilities=None,
    )
    inferred = infer_capabilities_from_profile(profile)
    assert "can_read_temp" in inferred

    async with async_session() as db:
        tenant_id = uuid.uuid4()
        legacy = Device(
            tenant_id=tenant_id,
            profile_id=None,
            name="Legacy node",
            device_type="lora_sensor",
            status=DeviceStatus.PENDING,
        )
        caps = await device_capabilities(db, legacy)
        assert "can_read_moisture" in caps
