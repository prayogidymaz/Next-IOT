from collections.abc import AsyncGenerator
from typing import Annotated, cast

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.types.redis_client import RedisClient


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_redis(request: Request) -> RedisClient:
    state_redis: object = getattr(request.app.state, "redis", None)
    if state_redis is None:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    if not isinstance(state_redis, aioredis.Redis):
        raise HTTPException(status_code=503, detail="Redis unavailable")
    return cast(RedisClient, state_redis)


DbSession = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[RedisClient, Depends(get_redis)]
