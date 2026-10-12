"""Agri firmware template API."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from tests.agriculture.conftest import register_tenant


@pytest.mark.asyncio
async def test_list_agri_firmware_templates(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await register_tenant(client, unique_slug, unique_email)
    token = str(reg["tokens"]["access_token"])
    listed = await client.get(
        "/api/v1/firmware-studio/agri-templates",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listed.status_code == 200
    names = listed.json()
    assert "agri_soil_sensor.cpp" in names
    body = await client.get(
        "/api/v1/firmware-studio/agri-templates/agri_soil_sensor.cpp",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert body.status_code == 200
    assert "LoRa" in body.text
