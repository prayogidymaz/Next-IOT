from fastapi import APIRouter
from pydantic import BaseModel

from app.auth.dependencies import RequireAuth
from app.auth.permissions import permissions_for_role

router = APIRouter(prefix="/api/v1/users", tags=["users"])


class UserPermissionsResponse(BaseModel):
    user_id: str
    tenant_id: str
    role: str
    permissions: list[str]


@router.get("/me/permissions", response_model=UserPermissionsResponse)
async def get_my_permissions(user: RequireAuth):
    return UserPermissionsResponse(
        user_id=str(user.user_id),
        tenant_id=str(user.tenant_id),
        role=user.role,
        permissions=permissions_for_role(user.role),
    )
