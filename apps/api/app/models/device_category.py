from enum import StrEnum


class DeviceCategory(StrEnum):
    """Operational domain taxonomy for fleet devices."""

    DRONE_UNMANNED = "DRONE_UNMANNED"
    AGRICULTURE_AQUACULTURE = "AGRICULTURE_AQUACULTURE"
    FIELD_SENSORS_LORA = "FIELD_SENSORS_LORA"
    INDUSTRIAL_TELEMETRY = "INDUSTRIAL_TELEMETRY"
    SMART_ASSET_FLEET = "SMART_ASSET_FLEET"
    SMART_HOME = "SMART_HOME"


def infer_device_category(device_type: str) -> DeviceCategory:
    normalized = device_type.strip().lower().replace("-", "_")
    if normalized in {"smart_home", "smart_home_building", "smarthome"}:
        return DeviceCategory.SMART_HOME
    if normalized in {"drone", "robot", "uav", "ugv"}:
        return DeviceCategory.DRONE_UNMANNED
    if normalized in {"lorawan", "lora", "lora_sensor"}:
        return DeviceCategory.FIELD_SENSORS_LORA
    if normalized in {"cyberdeck", "modbus_gateway", "industrial_gateway"}:
        return DeviceCategory.INDUSTRIAL_TELEMETRY
    if normalized in {"sensor", "multi_sensor", "aquaculture", "agriculture"}:
        return DeviceCategory.AGRICULTURE_AQUACULTURE
    if normalized in {"fleet", "vehicle", "asset_tracker"}:
        return DeviceCategory.SMART_ASSET_FLEET
    return DeviceCategory.FIELD_SENSORS_LORA
