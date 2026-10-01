"""Typed Redis asyncio client (decode_responses=True) and safe shutdown helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

import redis.asyncio as aioredis

if TYPE_CHECKING:
    # Stubs model Redis as generic; runtime redis-py does not subscript Redis.
    type RedisClient = aioredis.Redis[str]
else:
    RedisClient = aioredis.Redis


class RedisCloseable(Protocol):
    async def aclose(self) -> None: ...


class PubSubCloseable(Protocol):
    async def aclose(self) -> None: ...


async def close_redis(client: RedisClient) -> None:
    closeable = cast(RedisCloseable, client)
    await closeable.aclose()


async def close_pubsub(pubsub: object) -> None:
    closeable = cast(PubSubCloseable, pubsub)
    await closeable.aclose()


def redis_from_url(url: str) -> RedisClient:
    return aioredis.from_url(url, decode_responses=True)


def as_legacy_redis_stub(client: RedisClient) -> aioredis.Redis[str]:
    """Legacy packages still reference redis.asyncio.Redis in signatures (RATCHET burn-down)."""
    return client
