"""Shared fixtures for workflow Deep tests."""

from __future__ import annotations

import uuid

import pytest_asyncio
from app.auth.context import CurrentUser
from app.auth.tiering import SecurityTier
from app.database import async_session
from app.models.tenant import Tenant
from app.models.user import User


@pytest_asyncio.fixture
async def workflow_seed_user() -> User:
    async with async_session() as db:
        tenant = Tenant(name="Workflow Test", slug=f"wf-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        user = User(
            tenant_id=tenant.id,
            email=f"wf-{uuid.uuid4().hex[:8]}@example.com",
            password_hash="test-password-hash",
            role="tenant_admin",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


def workflow_current_user(user: User) -> CurrentUser:
    return CurrentUser(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        role=user.role,
        security_tier=SecurityTier.PRO,
    )
