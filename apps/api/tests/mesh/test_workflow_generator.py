"""WorkflowGenerator NL → WorkflowDraft tests."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from app.mesh.ai_copilot.draft_convert import draft_to_mesh_definition
from app.mesh.ai_copilot.nl_examples import NL_EXAMPLES, list_nl_examples
from app.mesh.ai_copilot.workflow_draft import DraftTriggerKind
from app.mesh.ai_copilot.workflow_generator import WorkflowGenerator
from app.mesh.workflow_schema import WorkflowTriggerType

PASSWORD = "SecurePass123!"


@pytest.mark.asyncio
async def test_generate_irrigation_workflow_id() -> None:
    gen = WorkflowGenerator(api_key="", model="claude-sonnet-4-5")
    draft = await gen.generate_from_nl(
        "kalau tanah plot A kering siram selama 15 menit",
        uuid.uuid4(),
        locale="id",
    )
    assert draft.trigger.kind == DraftTriggerKind.SENSOR_THRESHOLD
    assert draft.trigger.sensor == "soil_moisture"
    assert draft.actions[0].duration_minutes == 15


@pytest.mark.asyncio
async def test_generate_alert_workflow_id() -> None:
    gen = WorkflowGenerator(api_key="", model="claude-sonnet-4-5")
    draft = await gen.generate_from_nl("notif WA kalau pH tanah di bawah 5.5", uuid.uuid4())
    assert draft.actions[0].action == "notify"
    assert "whatsapp" in draft.actions[0].channels


@pytest.mark.asyncio
async def test_generate_scheduled_workflow_id() -> None:
    gen = WorkflowGenerator(api_key="", model="claude-sonnet-4-5")
    draft = await gen.generate_from_nl("siram plot B pagi hari jam 6", uuid.uuid4())
    assert draft.trigger.kind == DraftTriggerKind.CRON
    assert draft.trigger.cron == "0 6 * * *"


@pytest.mark.asyncio
async def test_mock_fallback_without_api_key() -> None:
    gen = WorkflowGenerator.from_settings()
    assert gen.mock_mode
    draft = await gen.generate_from_nl("nyalakan lampu greenhouse lux 300", uuid.uuid4())
    assert draft.source in {"mock", "few_shot"}
    assert draft.trigger.sensor == "lux" or draft.trigger.kind == DraftTriggerKind.SENSOR_THRESHOLD


@pytest.mark.asyncio
async def test_few_shot_exact_match() -> None:
    gen = WorkflowGenerator(api_key="", model="claude-sonnet-4-5")
    sample = NL_EXAMPLES[0].prompt_id
    draft = await gen.generate_from_nl(sample, uuid.uuid4())
    assert draft.source == "few_shot"


def test_nl_examples_count_bilingual() -> None:
    assert len(NL_EXAMPLES) == 50
    rows = list_nl_examples("id")
    assert len(rows) == 50
    rows_en = list_nl_examples("en")
    assert rows_en[0]["prompt"] == NL_EXAMPLES[0].prompt_en


@pytest.mark.asyncio
async def test_draft_convert_to_mesh_trigger() -> None:
    gen = WorkflowGenerator(api_key="", model="x")
    draft = await gen.generate_from_nl("siram plot A", uuid.uuid4())
    mesh = draft_to_mesh_definition(draft)
    assert mesh.trigger.type == WorkflowTriggerType.MESH_EVENT


@pytest.mark.asyncio
async def test_draft_convert_cron() -> None:
    gen = WorkflowGenerator(api_key="", model="x")
    draft = await gen.generate_from_nl("siram setiap pagi jam 6", uuid.uuid4())
    mesh = draft_to_mesh_definition(draft)
    assert mesh.trigger.type == WorkflowTriggerType.SCHEDULE


@pytest.mark.asyncio
async def test_generate_lux_light_workflow() -> None:
    gen = WorkflowGenerator(api_key="", model="x")
    draft = await gen.generate_from_nl(
        "nyalakan lampu greenhouse kalau cahaya kurang dari 300 lux",
        uuid.uuid4(),
    )
    assert draft.trigger.sensor == "lux" or draft.source == "few_shot"


@pytest.mark.asyncio
async def test_generate_webhook_mock() -> None:
    gen = WorkflowGenerator(api_key="", model="x")
    draft = await gen.generate_from_nl("webhook ke ERP saat yield turun", uuid.uuid4())
    assert draft.actions[0].action == "webhook" or draft.trigger.kind == DraftTriggerKind.EVENT


@pytest.mark.asyncio
async def test_commit_draft_creates_actual_workflow(
    client: AsyncClient,
    unique_slug: str,
    unique_email: str,
) -> None:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": "DraftCommit",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    token = reg.json()["tokens"]["access_token"]
    gen_resp = await client.post(
        "/api/v1/mesh/copilot/generate-workflow",
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": "kalau tanah plot A kering siram 15 menit", "locale": "id"},
    )
    assert gen_resp.status_code == 200
    draft_id = gen_resp.json()["draft"]["draft_id"]
    commit = await client.post(
        "/api/v1/mesh/copilot/commit-workflow",
        headers={"Authorization": f"Bearer {token}"},
        json={"draft_id": draft_id},
    )
    assert commit.status_code == 200
    assert commit.json()["workflow_id"]


@pytest.mark.asyncio
async def test_generate_workflow_endpoint(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": "GenWf",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    token = reg.json()["tokens"]["access_token"]
    resp = await client.post(
        "/api/v1/mesh/copilot/generate-workflow",
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": "notif WA pH rendah", "locale": "id"},
    )
    assert resp.status_code == 200
    body = resp.json()["draft"]
    assert body["draft_id"]
    assert len(body["actions"]) >= 1


@pytest.mark.asyncio
async def test_examples_locale_id_returns_fifty(
    client: AsyncClient,
    unique_slug: str,
    unique_email: str,
) -> None:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": "ExLocale",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    token = reg.json()["tokens"]["access_token"]
    resp = await client.get(
        "/api/v1/mesh/copilot/examples",
        params={"locale": "id"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 50


@pytest.mark.asyncio
async def test_commit_unknown_draft_404(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": "NoDraft",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    token = reg.json()["tokens"]["access_token"]
    resp = await client.post(
        "/api/v1/mesh/copilot/commit-workflow",
        headers={"Authorization": f"Bearer {token}"},
        json={"draft_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_generate_workflow_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/mesh/copilot/generate-workflow",
        json={"prompt": "siram plot A", "locale": "id"},
    )
    assert resp.status_code == 401
