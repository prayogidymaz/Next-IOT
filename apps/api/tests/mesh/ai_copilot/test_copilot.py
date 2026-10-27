"""Mesh AI Copilot tests."""

from __future__ import annotations

import pytest
from app.mesh.ai_copilot.client import LLMClient
from app.mesh.ai_copilot.examples import workflow_for_prompt
from app.mesh.ai_copilot.parser import parse_llm_workflow_payload
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


@pytest.mark.asyncio
async def test_mock_mode_returns_canned_workflow() -> None:
    client = LLMClient(api_key="", model="claude-sonnet-4-5")
    assert client.mock_mode
    result = await client.generate_workflow("Kalau soil moisture < 30%, buka irigasi", {})
    wf = result["workflow"]
    assert isinstance(wf, dict)
    assert wf["trigger"]["type"] == "mesh_event"


def test_parse_llm_response_valid_dsl() -> None:
    sample = workflow_for_prompt("drone hama")
    raw = sample.model_dump_json()
    parsed = parse_llm_workflow_payload(raw)
    assert parsed.name
    assert len(parsed.actions) >= 1


@pytest.mark.asyncio
async def test_router_generate_endpoint(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": "Copilot",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    token = reg.json()["tokens"]["access_token"]
    resp = await client.post(
        "/api/v1/mesh/copilot/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": "Kalau soil moisture < 30%, buka irigasi 15 menit"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["workflow"]["name"]
    assert body["confidence"] >= 0.5


@pytest.mark.asyncio
async def test_examples_endpoint(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": "Examples",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    token = reg.json()["tokens"]["access_token"]
    resp = await client.get(
        "/api/v1/mesh/copilot/examples",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 5
