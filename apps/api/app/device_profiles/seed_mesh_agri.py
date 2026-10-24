"""Seed Smart Farming mesh device profiles (Universal Mesh Phase 1)."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.device_profiles.spec import ThingModelSpec, spec_to_storage
from app.models.device_profile import DeviceProfile, ProfileDomain, ProfileStatus
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)

_MESH_AGRI_PROFILES: list[tuple[str, str, list[str]]] = [
    (
        "agri_sensor_v2",
        "Agriculture sensor v2 (mesh)",
        ["can_read_moisture", "can_read_npk", "can_read_ph", "can_read_temp"],
    ),
    (
        "agri_cctv_outdoor",
        "Outdoor agriculture CCTV",
        ["can_capture_image", "can_capture_video", "can_detect_motion", "can_run_edge_ai"],
    ),
    (
        "agri_drone_patrol",
        "Agriculture patrol drone",
        [
            "can_fly_to",
            "can_hover",
            "can_takeoff_rth",
            "can_land",
            "can_capture_image",
            "can_capture_ndvi",
            "can_capture_thermal",
        ],
    ),
    (
        "agri_sprayer_station",
        "Sprayer / valve station",
        ["can_control_valve", "can_spray", "can_report_tank_level"],
    ),
    (
        "agri_cyberdeck_field",
        "Field cyberdeck console",
        ["can_display_dashboard", "can_remote_control", "can_lora_bridge", "can_quick_action"],
    ),
    (
        "agri_gate_lock",
        "Farm gate lock",
        ["can_lock", "can_unlock", "can_detect_proximity", "can_sound_alarm"],
    ),
    (
        "agri_weather_station",
        "Weather station",
        ["can_report_temp", "can_report_humidity", "can_report_weather", "can_predict_weather"],
    ),
]


def _empty_spec() -> dict[str, object]:
    return spec_to_storage(ThingModelSpec(telemetry=[], attributes=[], commands=[]))


async def ensure_mesh_agri_device_profiles(db: AsyncSession) -> int:
    tenant = await db.scalar(select(Tenant).where(Tenant.slug == settings.seed_tenant_slug))
    if tenant is None:
        return 0

    created = 0
    for key, name, capabilities in _MESH_AGRI_PROFILES:
        existing = await db.scalar(
            select(DeviceProfile.id).where(
                DeviceProfile.tenant_id == tenant.id,
                DeviceProfile.key == key,
                DeviceProfile.version == 1,
            )
        )
        if existing is not None:
            continue
        db.add(
            DeviceProfile(
                tenant_id=tenant.id,
                key=key,
                name=name,
                description=f"Mesh seed profile: {name}",
                domain=ProfileDomain.SMART_FARMING.value,
                version=1,
                status=ProfileStatus.PUBLISHED,
                spec=_empty_spec(),
                capabilities=capabilities,
            )
        )
        created += 1

    if created:
        await db.commit()
        logger.info("Seeded %s mesh agri device profile(s) for tenant %s", created, settings.seed_tenant_slug)
    return created


async def run_mesh_agri_profile_seed() -> int:
    from app.database import async_session

    async with async_session() as db:
        return await ensure_mesh_agri_device_profiles(db)
