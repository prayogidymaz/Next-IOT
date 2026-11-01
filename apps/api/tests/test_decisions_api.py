"""Decisions API scaffold — enable after migration 055."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.skip(reason="Scaffold: run manually after alembic upgrade head")


@pytest.mark.asyncio
async def test_decisions_unauthorized(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/decisions/recommendations")).status_code == 401
