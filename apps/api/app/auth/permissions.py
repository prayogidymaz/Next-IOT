from app.auth.rbac import UserRole

# Fine-grained permission strings for dashboard RBAC guards.
PERMISSION_DEVICES_READ = "devices.read"
PERMISSION_DEVICES_REGISTER = "devices.register"
PERMISSION_DEVICES_DELETE = "devices.delete"
PERMISSION_OTA_UPLOAD = "ota.upload"
PERMISSION_COMMANDS_SEND = "commands.send"
PERMISSION_ALERTS_MANAGE = "alerts.manage"
PERMISSION_ALERTS_ACK = "alerts.ack"
PERMISSION_SETTINGS_MANAGE = "settings.manage"
PERMISSION_TENANT_MANAGE = "tenant.manage"
PERMISSION_MEMBERS_MANAGE = "members.manage"
PERMISSION_AUTOMATION_READ = "automation.read"
PERMISSION_AUTOMATION_MANAGE = "automation.manage"
PERMISSION_AUTOMATION_RUN = "automation.run"
PERMISSION_AUDIT_READ = "audit.read"

ALL_PERMISSIONS = frozenset(
    {
        PERMISSION_DEVICES_READ,
        PERMISSION_DEVICES_REGISTER,
        PERMISSION_DEVICES_DELETE,
        PERMISSION_OTA_UPLOAD,
        PERMISSION_COMMANDS_SEND,
        PERMISSION_ALERTS_MANAGE,
        PERMISSION_ALERTS_ACK,
        PERMISSION_SETTINGS_MANAGE,
        PERMISSION_TENANT_MANAGE,
        PERMISSION_MEMBERS_MANAGE,
        PERMISSION_AUTOMATION_READ,
        PERMISSION_AUTOMATION_MANAGE,
        PERMISSION_AUTOMATION_RUN,
        PERMISSION_AUDIT_READ,
    }
)

_ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    UserRole.VIEWER: frozenset(
        {
            PERMISSION_DEVICES_READ,
            PERMISSION_AUTOMATION_READ,
            PERMISSION_AUTOMATION_RUN,
        }
    ),
    UserRole.OPERATOR: frozenset(
        {
            PERMISSION_DEVICES_READ,
            PERMISSION_COMMANDS_SEND,
            PERMISSION_ALERTS_ACK,
            PERMISSION_AUTOMATION_READ,
            PERMISSION_AUTOMATION_RUN,
        }
    ),
    UserRole.TENANT_ADMIN: frozenset(ALL_PERMISSIONS),
    UserRole.SUPER_ADMIN: frozenset(ALL_PERMISSIONS),
}


def permissions_for_role(role: str) -> list[str]:
    normalized = role.lower()
    perms = _ROLE_PERMISSIONS.get(normalized, frozenset())
    return sorted(perms)


def role_has_permission(role: str, permission: str) -> bool:
    return permission in _ROLE_PERMISSIONS.get(role.lower(), frozenset())
