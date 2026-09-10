import redis.asyncio as aioredis
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_redis(request: Request) -> aioredis.Redis:
    redis = request.app.state.redis
    if redis is None:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    return redis
