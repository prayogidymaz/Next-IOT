import uuid

from sqlalchemy import true
from sqlalchemy.sql.elements import ColumnElement

from app.auth.dependencies import CurrentUser


def scoped_tenant_id(user: CurrentUser, requested_tenant_id: uuid.UUID) -> uuid.UUID:
    """Return the tenant_id the user is allowed to access for the given request."""
    if user.is_super_admin:
        return requested_tenant_id
    if user.tenant_id != requested_tenant_id:
        raise PermissionError("Tenant isolation violation")
    return user.tenant_id


def tenant_filter_clause(user: CurrentUser, tenant_column: ColumnElement) -> ColumnElement:
    """Build SQLAlchemy WHERE clause scoped to the user's tenant."""
    if user.is_super_admin:
        return true()
    return tenant_column == user.tenant_id
