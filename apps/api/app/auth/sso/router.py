"""SSO configuration routes."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.auth.dependencies import RequireTenantAdmin
from app.auth.sso import service
from app.auth.sso.models import SsoConfig
from app.deps import DbSession
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/auth/sso", tags=["sso"])


class SsoConfigView(BaseModel):
    provider: str
    client_id: str
    enabled: bool
    metadata_json: dict[str, object]

    model_config = {"from_attributes": True}


class SsoUpsertBody(BaseModel):
    provider: str = Field(pattern=r"^(google|microsoft|okta|saml)$")
    client_id: str
    client_secret: str = ""
    enabled: bool = False


@router.get("", response_model=list[SsoConfigView])
async def list_sso(user: RequireTenantAdmin, db: DbSession) -> list[SsoConfigView]:
    rows = await service.list_sso_configs(db, user)
    return [_view(r) for r in rows]


@router.put("/{provider}", response_model=SsoConfigView)
async def upsert_sso(user: RequireTenantAdmin, db: DbSession, provider: str, body: SsoUpsertBody) -> SsoConfigView:
    row = await service.upsert_sso_config(db, user, provider, body.client_id, body.client_secret, body.enabled)
    return _view(row)


def _view(row: SsoConfig) -> SsoConfigView:
    return SsoConfigView(
        provider=row.provider,
        client_id=row.client_id,
        enabled=row.enabled,
        metadata_json=row.metadata_json if isinstance(row.metadata_json, dict) else {},
    )
