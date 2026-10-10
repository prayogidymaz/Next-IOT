"""Role dependencies for device HTTP routes."""

from typing import Annotated

from fastapi import Depends

from app.auth.context import CurrentUser
from app.auth.dependencies import require_roles
from app.auth.rbac import UserRole

RequireDeviceReader = Annotated[
    CurrentUser,
    Depends(require_roles(UserRole.VIEWER, UserRole.OPERATOR, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN)),
]
