"""SSO setup (Google / Microsoft OAuth2 templates; SAML TODO)."""

from __future__ import annotations

import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.auth.sso.models import SsoConfig

logger = logging.getLogger(__name__)

OAUTH_TEMPLATES: dict[str, dict[str, str]] = {
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": "openid email profile",
    },
    "microsoft": {
        "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "scopes": "openid email profile",
    },
    # SAML: integrate python3-saml or similar — not in scope for this batch.
}


async def list_sso_configs(db: AsyncSession, user: CurrentUser) -> list[SsoConfig]:
    rows = await db.scalars(select(SsoConfig).where(SsoConfig.tenant_id == user.tenant_id))
    return list(rows.all())


async def upsert_sso_config(
    db: AsyncSession,
    user: CurrentUser,
    provider: str,
    client_id: str,
    client_secret: str,
    enabled: bool,
) -> SsoConfig:
    if provider not in {"google", "microsoft", "okta", "saml"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider")
    if provider == "saml":
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="SAML SSO TODO — use metadata_json when implemented")
    template = OAUTH_TEMPLATES.get(provider, {})
    row = await db.scalar(
        select(SsoConfig).where(SsoConfig.tenant_id == user.tenant_id, SsoConfig.provider == provider)
    )
    if row is None:
        row = SsoConfig(
            tenant_id=user.tenant_id,
            provider=provider,
            client_id=client_id,
            client_secret_encrypted=client_secret,
            metadata_json=template,
            enabled=enabled,
        )
        db.add(row)
    else:
        row.client_id = client_id
        if client_secret:
            row.client_secret_encrypted = client_secret
        row.metadata_json = {**template, **row.metadata_json}
        row.enabled = enabled
    await db.commit()
    await db.refresh(row)
    return row
