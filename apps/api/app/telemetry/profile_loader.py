"""Load published thing-model specs for devices (async DB)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.device_profiles.spec import ThingModelSpec, parse_thing_model_spec
from app.models.device import Device
from app.models.device_profile import DeviceProfile


async def load_thing_model_for_device(
    db: AsyncSession,
    device: Device,
) -> ThingModelSpec | None:
    if device.profile_id is None:
        return None
    profile = await db.scalar(select(DeviceProfile).where(DeviceProfile.id == device.profile_id))
    if profile is None:
        return None
    return parse_thing_model_spec(profile.spec)
