"""Reports API scaffold — enable after migration 054."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.skip(reason="Scaffold: run manually after alembic upgrade head")


@pytest.mark.asyncio
async def test_reports_unauthorized(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/reports/templates")).status_code == 401
