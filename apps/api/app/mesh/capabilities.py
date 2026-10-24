"""Standardized device capability keys for the Universal Device Mesh."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.device_profile import DeviceProfile

CAPABILITY_KEYS: frozenset[str] = frozenset(
    {
        "can_read_moisture",
        "can_read_npk",
        "can_read_ph",
        "can_read_temp",
        "can_read_humidity",
        "can_read_pressure",
        "can_read_light",
        "can_capture_image",
        "can_capture_video",
        "can_detect_motion",
        "can_run_edge_ai",
        "can_capture_ndvi",
        "can_capture_thermal",
        "can_fly_to",
        "can_hover",
        "can_takeoff_rth",
        "can_land",
        "can_control_valve",
        "can_spray",
        "can_control_relay",
        "can_dim",
        "can_set_color_rgb",
        "can_rotate_stepper",
        "can_lock",
        "can_unlock",
        "can_detect_proximity",
        "can_sound_alarm",
        "can_display_dashboard",
        "can_display_alert",
        "can_display_lvgl_widget",
        "can_vibrate_haptic",
        "can_quick_action",
        "can_lora_bridge",
        "can_lora_fallback",
        "can_relay_to_mobile",
        "can_remote_control",
        "can_report_weather",
        "can_predict_weather",
        "can_report_tank_level",
        "can_report_temp",
        "can_report_humidity",
    }
)

_PROFILE_KEY_CAPABILITIES: dict[str, list[str]] = {
    "agri_sensor": ["can_read_moisture", "can_read_npk", "can_read_ph", "can_read_temp"],
    "agri_sensor_v2": ["can_read_moisture", "can_read_npk", "can_read_ph", "can_read_temp"],
    "agri_cctv_outdoor": [
        "can_capture_image",
        "can_capture_video",
        "can_detect_motion",
        "can_run_edge_ai",
    ],
    "agri_drone_patrol": [
        "can_fly_to",
        "can_hover",
        "can_takeoff_rth",
        "can_land",
        "can_capture_image",
        "can_capture_ndvi",
        "can_capture_thermal",
    ],
    "agri_sprayer_station": ["can_control_valve", "can_spray", "can_report_tank_level"],
    "agri_cyberdeck_field": [
        "can_display_dashboard",
        "can_remote_control",
        "can_lora_bridge",
        "can_quick_action",
    ],
    "agri_gate_lock": ["can_lock", "can_unlock", "can_detect_proximity", "can_sound_alarm"],
    "agri_weather_station": [
        "can_report_temp",
        "can_report_humidity",
        "can_report_weather",
        "can_predict_weather",
    ],
    "env_sensor": ["can_read_temp", "can_read_humidity"],
    "smart_switch": ["can_control_relay"],
    "smart_lock": ["can_lock", "can_unlock"],
}

_LEGACY_DEVICE_TYPE_CAPABILITIES: dict[str, list[str]] = {
    "lora_sensor": ["can_read_moisture", "can_read_temp"],
    "sensor": ["can_read_moisture", "can_read_temp"],
    "agriculture": ["can_read_moisture", "can_read_npk"],
    "drone": ["can_fly_to", "can_hover", "can_capture_image"],
    "lorawan": ["can_read_moisture", "can_lora_bridge"],
    "cctv": ["can_capture_image", "can_capture_video", "can_detect_motion"],
    "weather_station": ["can_report_weather", "can_report_temp", "can_report_humidity"],
}


def validate_capability(key: str) -> bool:
    return key in CAPABILITY_KEYS


def _normalize_capability_list(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if isinstance(item, str) and validate_capability(item):
            out.append(item)
    return out


def infer_capabilities_from_profile(profile: DeviceProfile | None) -> list[str]:
    if profile is None:
        return []
    explicit = _normalize_capability_list(profile.capabilities)
    if explicit:
        return explicit
    mapped = _PROFILE_KEY_CAPABILITIES.get(profile.key)
    if mapped is not None:
        return list(mapped)
    return []


def infer_capabilities_from_device_type(device_type: str) -> list[str]:
    normalized = device_type.strip().lower().replace("-", "_")
    return list(_LEGACY_DEVICE_TYPE_CAPABILITIES.get(normalized, []))


async def device_capabilities(db: AsyncSession, device: Device) -> list[str]:
    if device.profile_id is not None:
        profile = await db.scalar(select(DeviceProfile).where(DeviceProfile.id == device.profile_id))
        caps = infer_capabilities_from_profile(profile)
        if caps:
            return caps
    return infer_capabilities_from_device_type(device.device_type)


async def devices_with_capability(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    capability_key: str,
) -> list[Device]:
    if not validate_capability(capability_key):
        return []
    rows = await db.scalars(select(Device).where(Device.tenant_id == tenant_id))
    matched: list[Device] = []
    for device in rows.all():
        caps = await device_capabilities(db, device)
        if capability_key in caps:
            matched.append(device)
    return matched
