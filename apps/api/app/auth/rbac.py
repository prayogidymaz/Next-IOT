from enum import StrEnum


class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


VALID_ROLES = frozenset(UserRole)

# Roles that may mutate resources (non read-only)
WRITE_ROLES = frozenset({UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN, UserRole.OPERATOR})

# Roles with tenant-wide admin privileges
ADMIN_ROLES = frozenset({UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN})


def has_role(user_role: str, allowed_roles: set[str | UserRole]) -> bool:
    normalized = {str(r) for r in allowed_roles}
    return user_role in normalized


def is_super_admin(user_role: str) -> bool:
    return user_role == UserRole.SUPER_ADMIN
