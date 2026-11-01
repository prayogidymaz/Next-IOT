"""Webhooks API — run manually after migration 050."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.skip(reason="Scaffold: enable after alembic upgrade head")


@pytest.mark.asyncio
async def test_webhook_crud_unauthorized(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/webhooks")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_webhook_test_send(client: AsyncClient) -> None:
    """TODO: create webhook, POST /test, assert delivered flag."""
    assert True
