"""Idempotent seed for default platform admin (dev / docker startup)."""

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import hash_password
from app.config import settings
from app.database import async_session
from app.models.tenant import Tenant
from app.models.user import User

logger = logging.getLogger(__name__)


async def ensure_default_admin(db: AsyncSession) -> bool:
    """Create default tenant + super_admin if missing. Returns True when created."""
    existing_user = await db.scalar(select(User).where(User.email == settings.seed_admin_email))
    if existing_user:
        logger.debug("Seed skipped: %s already exists", settings.seed_admin_email)
        return False

    tenant = await db.scalar(select(Tenant).where(Tenant.slug == settings.seed_tenant_slug))
    if tenant is None:
        tenant = Tenant(name=settings.seed_tenant_name, slug=settings.seed_tenant_slug)
        db.add(tenant)
        await db.flush()

    user = User(
        tenant=tenant,
        email=settings.seed_admin_email,
        password_hash=hash_password(settings.seed_admin_password),
        role="super_admin",
    )
    db.add(user)
    await db.commit()
    logger.info(
        "Seeded default admin %s (tenant=%s, role=super_admin)",
        settings.seed_admin_email,
        settings.seed_tenant_slug,
    )
    return True


async def run_seed() -> bool:
    async with async_session() as db:
        return await ensure_default_admin(db)


def main() -> None:
    created = asyncio.run(run_seed())
    if created:
        print(f"Created default admin: {settings.seed_admin_email}")
    else:
        print(f"Default admin already exists: {settings.seed_admin_email}")


if __name__ == "__main__":
    main()
