#!/usr/bin/env python3
"""Bootstrap a platform super_admin user (run inside api container or with DATABASE_URL set)."""

from __future__ import annotations

import argparse
import asyncio
import uuid

from sqlalchemy import select

from app.auth.rbac import UserRole
from app.auth.security import hash_password
from app.database import async_session
from app.models.tenant import Tenant
from app.models.tenant_membership import TenantMembership
from app.models.user import User


async def _create(email: str, password: str, tenant_slug: str) -> None:
    async with async_session() as db:
        existing = await db.scalar(select(User).where(User.email == email))
        if existing is not None:
            print(f"User already exists: {email}")
            return
        tenant = await db.scalar(select(Tenant).where(Tenant.slug == tenant_slug))
        if tenant is None:
            tenant = Tenant(name="Platform", slug=tenant_slug)
            db.add(tenant)
            await db.flush()
        user = User(
            tenant_id=tenant.id,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.SUPER_ADMIN,
        )
        db.add(user)
        await db.flush()
        db.add(
            TenantMembership(
                user_id=user.id,
                tenant_id=tenant.id,
                role=UserRole.SUPER_ADMIN,
            )
        )
        await db.commit()
        print(f"Created super_admin {email} tenant={tenant.slug} id={user.id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--tenant-slug", default="nextiot")
    args = parser.parse_args()
    asyncio.run(_create(args.email, args.password, args.tenant_slug))


if __name__ == "__main__":
    main()
