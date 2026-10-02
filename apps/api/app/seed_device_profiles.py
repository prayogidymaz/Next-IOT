"""Idempotent published thing-model profiles for the default seed tenant."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.device_profiles.spec import (
    AttributeDefNumber,
    AttributeScope,
    CommandDef,
    CommandParamBoolean,
    TelemetryKeyBoolean,
    TelemetryKeyEnum,
    TelemetryKeyInteger,
    TelemetryKeyNumber,
    ThingModelSpec,
    spec_to_storage,
)
from app.models.device_profile import DeviceProfile, ProfileDomain, ProfileStatus
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


def _smart_switch_spec() -> ThingModelSpec:
    return ThingModelSpec(
        telemetry=[
            TelemetryKeyBoolean(key="relay_on", label="Relay state", data_type="boolean"),
        ],
        attributes=[],
        commands=[
            CommandDef(key="turn_on", label="Turn relay on", params=[]),
            CommandDef(key="turn_off", label="Turn relay off", params=[]),
        ],
    )


def _env_sensor_spec() -> ThingModelSpec:
    return ThingModelSpec(
        telemetry=[
            TelemetryKeyNumber(
                key="temperature", label="Temperature", unit="C", data_type="number", min=-40, max=85
            ),
            TelemetryKeyNumber(
                key="humidity", label="Humidity", unit="%", data_type="number", min=0, max=100
            ),
            TelemetryKeyInteger(
                key="battery", label="Battery", unit="%", data_type="integer", min=0, max=100
            ),
            TelemetryKeyInteger(
                key="rssi", label="RSSI", unit="dBm", data_type="integer", min=-120, max=0
            ),
        ],
        attributes=[
            AttributeDefNumber(
                key="report_interval_sec",
                label="Report interval",
                scope=AttributeScope.SHARED,
                data_type="number",
                default=60,
                min=10,
                max=3600,
            ),
        ],
        commands=[],
    )


def _smart_lock_spec() -> ThingModelSpec:
    return ThingModelSpec(
        telemetry=[
            TelemetryKeyEnum(
                key="lock_state", label="Lock state", data_type="enum", values=["locked", "unlocked"]
            ),
            TelemetryKeyInteger(
                key="battery", label="Battery", unit="%", data_type="integer", min=0, max=100
            ),
        ],
        attributes=[],
        commands=[
            CommandDef(key="lock", label="Lock door", params=[]),
            CommandDef(key="unlock", label="Unlock door", params=[]),
            CommandDef(
                key="set_auto_lock",
                label="Enable auto lock",
                params=[CommandParamBoolean(key="enabled", data_type="boolean", required=True)],
            ),
        ],
    )


_SEED_PROFILES: list[tuple[str, str, ProfileDomain, ThingModelSpec]] = [
    ("smart_switch", "Smart Switch", ProfileDomain.SMART_HOME, _smart_switch_spec()),
    ("env_sensor", "Environment Sensor", ProfileDomain.SMART_HOME, _env_sensor_spec()),
    ("smart_lock", "Smart Lock", ProfileDomain.SMART_HOME, _smart_lock_spec()),
]


async def ensure_demo_device_profiles(db: AsyncSession) -> int:
    tenant = await db.scalar(select(Tenant).where(Tenant.slug == settings.seed_tenant_slug))
    if tenant is None:
        return 0

    created = 0
    for key, name, domain, spec in _SEED_PROFILES:
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
                description=f"Seed profile: {name}",
                domain=domain.value,
                version=1,
                status=ProfileStatus.PUBLISHED,
                spec=spec_to_storage(spec),
            )
        )
        created += 1

    if created:
        await db.commit()
        logger.info("Seeded %s demo device profile(s) for tenant %s", created, settings.seed_tenant_slug)
    return created


async def run_device_profile_seed() -> int:
    from app.database import async_session

    async with async_session() as db:
        return await ensure_demo_device_profiles(db)
