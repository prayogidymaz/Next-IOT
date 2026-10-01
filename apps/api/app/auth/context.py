import uuid
from dataclasses import dataclass

from app.auth.rbac import is_super_admin
from app.auth.tiering import SecurityTier


@dataclass(frozen=True)
class CurrentUser:
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    role: str
    security_tier: SecurityTier

    @property
    def is_super_admin(self) -> bool:
        return is_super_admin(self.role)
