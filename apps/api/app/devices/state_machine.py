from app.models.device import DeviceStatus

# Valid admin transitions via PATCH /status
ADMIN_STATUS_TARGETS = frozenset(
    {DeviceStatus.PROVISIONED, DeviceStatus.DEACTIVATED}
)

HEARTBEAT_ALLOWED_STATUSES = frozenset(
    {DeviceStatus.PROVISIONED, DeviceStatus.ONLINE, DeviceStatus.OFFLINE}
)


def can_send_heartbeat(status: str) -> bool:
    return status in HEARTBEAT_ALLOWED_STATUSES


def should_emit_online(previous_status: str, new_status: str) -> bool:
    return new_status == DeviceStatus.ONLINE and previous_status != DeviceStatus.ONLINE
