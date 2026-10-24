"""Resolve devices by capability, zone, and geo proximity."""

from __future__ import annotations

import logging
import math
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agriculture.models import AgriSensorDevice
from app.mesh.capabilities import devices_with_capability
from app.mesh.context_resolver import resolve_device_context
from app.mesh.workflow_schema import DeviceResolverSpec
from app.mesh.workflow_templates import render_json_object, render_json_value
from app.models.device import Device
from app.models.device_attribute import DeviceAttribute
from app.models.device_profile import DeviceProfile
from app.types.json_types import JsonObject, JsonValue
from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _geo_from_spec(spec: JsonObject | str | None) -> tuple[float, float] | None:
    if spec is None or isinstance(spec, str):
        return None
    lat = spec.get("lat")
    lng = spec.get("lng")
    if isinstance(lat, int | float) and isinstance(lng, int | float):
        return float(lat), float(lng)
    return None


async def _device_geo(
    db: AsyncSession, redis: RedisClient, device: Device
) -> tuple[float, float] | None:
    ctx = await resolve_device_context(db, redis, device.id)
    if ctx.geo_location is not None:
        return ctx.geo_location.lat, ctx.geo_location.lng
    return None


async def device_matches_state(
    db: AsyncSession,
    device: Device,
    state_match: JsonObject,
) -> bool:
    for key, expected in state_match.items():
        actual: JsonValue
        if key == "status":
            actual = device.status
        else:
            row = await db.scalar(
                select(DeviceAttribute).where(
                    DeviceAttribute.device_id == device.id,
                    DeviceAttribute.key == key,
                )
            )
            if row is None:
                actual = None
            else:
                stored = row.value_json
                if isinstance(stored, str | int | float | bool) or stored is None:
                    actual = stored
                elif isinstance(stored, dict):
                    actual = stored
                else:
                    actual = str(stored)
        if not _value_matches(actual, expected):
            return False
    return True


def _value_matches(actual: JsonValue, expected: JsonValue) -> bool:
    if isinstance(expected, dict):
        if not isinstance(actual, int | float):
            return False
        for op, bound in expected.items():
            if op == "$gte" and isinstance(bound, int | float) and float(actual) < float(bound):
                return False
            if op == "$lte" and isinstance(bound, int | float) and float(actual) > float(bound):
                return False
            if op == "$eq" and actual != bound:
                return False
        return True
    return actual == expected


def _render_resolver_spec(spec: DeviceResolverSpec, template_context: JsonObject) -> DeviceResolverSpec:
    raw = spec.model_dump(mode="json")
    rendered = render_json_object(raw, template_context)
    return DeviceResolverSpec.model_validate(rendered)


async def _filter_devices(
    db: AsyncSession,
    redis: RedisClient,
    tenant_id: uuid.UUID,
    spec: DeviceResolverSpec,
    template_context: JsonObject,
) -> list[Device]:
    resolved_spec = _render_resolver_spec(spec, template_context)
    if resolved_spec.device_id is not None:
        device_uuid: uuid.UUID | None
        if isinstance(resolved_spec.device_id, uuid.UUID):
            device_uuid = resolved_spec.device_id
        else:
            try:
                device_uuid = uuid.UUID(str(resolved_spec.device_id))
            except ValueError:
                return []
        device = await db.scalar(
            select(Device).where(Device.id == device_uuid, Device.tenant_id == tenant_id)
        )
        return [device] if device is not None else []

    capability = resolved_spec.capability
    if capability is None:
        return []
    candidates = await devices_with_capability(db, tenant_id, capability)
    filtered: list[Device] = []
    for device in candidates:
        if resolved_spec.farm_id is not None or resolved_spec.plot_id is not None:
            agri = await db.scalar(select(AgriSensorDevice).where(AgriSensorDevice.device_id == device.id))
            if resolved_spec.farm_id is not None and (agri is None or agri.farm_id != resolved_spec.farm_id):
                continue
            if resolved_spec.plot_id is not None and (agri is None or agri.plot_id != resolved_spec.plot_id):
                continue
        if resolved_spec.zone is not None:
            zone_match = False
            if device.profile_id is not None:
                profile = await db.scalar(select(DeviceProfile).where(DeviceProfile.id == device.profile_id))
                if profile is not None and profile.physical_zone == resolved_spec.zone:
                    zone_match = True
            ctx = await resolve_device_context(db, redis, device.id)
            if ctx.physical_zone == resolved_spec.zone:
                zone_match = True
            if not zone_match:
                continue
        if resolved_spec.state_match is not None and not await device_matches_state(
            db, device, resolved_spec.state_match
        ):
            continue
        filtered.append(device)
    target = _geo_from_spec(resolved_spec.nearest_to)
    if target is not None:
        scored: list[tuple[float, Device]] = []
        for device in filtered:
            geo = await _device_geo(db, redis, device)
            if geo is None:
                continue
            dist = haversine_km(target[0], target[1], geo[0], geo[1])
            scored.append((dist, device))
        scored.sort(key=lambda item: item[0])
        return [device for _, device in scored]
    return filtered


async def resolve_device(
    db: AsyncSession,
    redis: RedisClient,
    tenant_id: uuid.UUID,
    resolver_spec: DeviceResolverSpec,
    template_context: JsonObject | None = None,
) -> Device | None:
    ctx = template_context or {}
    matches = await _filter_devices(db, redis, tenant_id, resolver_spec, ctx)
    if not matches:
        logger.info("device_resolver found no match tenant_id=%s capability=%s", tenant_id, resolver_spec.capability)
        return None
    return matches[0]


async def resolve_devices_multi(
    db: AsyncSession,
    redis: RedisClient,
    tenant_id: uuid.UUID,
    resolver_spec: DeviceResolverSpec,
    template_context: JsonObject | None = None,
) -> list[Device]:
    ctx = template_context or {}
    return await _filter_devices(db, redis, tenant_id, resolver_spec, ctx)


async def resolve_device_id_template(
    _db: AsyncSession,
    _tenant_id: uuid.UUID,
    device_ref: str,
    template_context: JsonObject,
) -> uuid.UUID | None:
    rendered = render_json_value(device_ref, template_context)
    if isinstance(rendered, str):
        try:
            return uuid.UUID(rendered)
        except ValueError:
            return None
    return None
