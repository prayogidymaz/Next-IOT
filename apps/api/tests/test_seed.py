import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.auth.security import verify_password
from app.config import settings
from app.database import async_session
from app.models.user import User
from app.seed import ensure_default_admin


@pytest.mark.asyncio
async def test_seed_creates_default_super_admin(client: AsyncClient):
    async with async_session() as db:
        created = await ensure_default_admin(db)
        assert created is True

        user = await db.scalar(select(User).where(User.email == settings.seed_admin_email))
        assert user is not None
        assert user.role == "super_admin"
        assert verify_password(settings.seed_admin_password, user.password_hash)

        created_again = await ensure_default_admin(db)
        assert created_again is False


@pytest.mark.asyncio
async def test_seed_admin_can_login(client: AsyncClient):
    async with async_session() as db:
        await ensure_default_admin(db)

    login = await client.post(
        "/auth/login",
        json={"email": settings.seed_admin_email, "password": settings.seed_admin_password},
    )
    assert login.status_code == 200
    body = login.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"
