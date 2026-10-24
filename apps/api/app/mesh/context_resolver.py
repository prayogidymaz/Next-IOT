"""Resolve mesh context for a platform device."""

from __future__ import annotations

import json
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agriculture.models import AgriSensorDevice
from app.mesh.capabilities import device_capabilities
from app.mesh.schemas import GeoLocation, MeshContext
from app.models.device import Device
from app.models.device_profile import DeviceProfile
from app.types.redis_client import RedisClient

_CONTEXT_CACHE_PREFIX = "mesh:ctx:"
_CONTEXT_CACHE_TTL_SECONDS = 60


def _cache_key(device_id: uuid.UUID) -> str:
    return f"{_CONTEXT_CACHE_PREFIX}{device_id}"


async def invalidate_device_context_cache(redis: RedisClient, device_id: uuid.UUID) -> None:
    await redis.delete(_cache_key(device_id))


async def invalidate_context_for_profile(
    redis: RedisClient, db: AsyncSession, profile_id: uuid.UUID
) -> None:
    rows = await db.scalars(select(Device.id).where(Device.profile_id == profile_id))
    for device_id in rows.all():
        await invalidate_device_context_cache(redis, device_id)


async def resolve_device_context(
    db: AsyncSession,
    redis: RedisClient,
    device_id: uuid.UUID,
) -> MeshContext:
    cached = await redis.get(_cache_key(device_id))
    if isinstance(cached, str) and cached:
        parsed = json.loads(cached)
        return MeshContext.model_validate(parsed)

    device = await db.scalar(select(Device).where(Device.id == device_id))
    if device is None:
        return MeshContext()

    farm_id: uuid.UUID | None = None
    plot_id: uuid.UUID | None = None
    geo: GeoLocation | None = None
    physical_zone: str | None = None

    profile: DeviceProfile | None = None
    if device.profile_id is not None:
        profile = await db.scalar(select(DeviceProfile).where(DeviceProfile.id == device.profile_id))
        if profile is not None:
            physical_zone = profile.physical_zone
            if isinstance(profile.geo_location, dict):
                lat = profile.geo_location.get("lat")
                lng = profile.geo_location.get("lng")
                if isinstance(lat, int | float) and isinstance(lng, int | float):
                    geo = GeoLocation(lat=float(lat), lng=float(lng))

    agri_sensor = await db.scalar(select(AgriSensorDevice).where(AgriSensorDevice.device_id == device_id))
    if agri_sensor is not None:
        farm_id = agri_sensor.farm_id
        plot_id = agri_sensor.plot_id
        if geo is None and agri_sensor.position_lat is not None and agri_sensor.position_lng is not None:
            geo = GeoLocation(lat=float(agri_sensor.position_lat), lng=float(agri_sensor.position_lng))

    capabilities = await device_capabilities(db, device)
    context = MeshContext(
        farm_id=farm_id,
        plot_id=plot_id,
        geo_location=geo,
        physical_zone=physical_zone,
        capabilities=capabilities,
    )
    await redis.setex(_cache_key(device_id), _CONTEXT_CACHE_TTL_SECONDS, context.model_dump_json())
    return context
