"""Mesh AI Copilot HTTP API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.auth.dependencies import RequireAuth
from app.deps import DbSession, RedisDep
from app.mesh.ai_copilot.draft_convert import draft_to_mesh_definition
from app.mesh.ai_copilot.draft_store import delete_draft, load_draft, save_draft
from app.mesh.ai_copilot.examples import list_examples
from app.mesh.ai_copilot.nl_examples import list_nl_examples
from app.mesh.ai_copilot.schemas import (
    CopilotCommitWorkflowRequest,
    CopilotCommitWorkflowResponse,
    CopilotExampleItem,
    CopilotExplainRequest,
    CopilotExplainResponse,
    CopilotGenerateRequest,
    CopilotGenerateResponse,
    CopilotGenerateWorkflowRequest,
    CopilotGenerateWorkflowResponse,
    CopilotNlExampleItem,
)
from app.mesh.ai_copilot.service import explain_workflow, generate_workflow_from_prompt
from app.mesh.ai_copilot.workflow_draft import WorkflowDraft
from app.mesh.ai_copilot.workflow_generator import WorkflowGenerator
from app.mesh.workflow_schema import MeshWorkflowDefinition
from app.mesh.workflow_service import create_workflow

router = APIRouter(prefix="/api/v1/mesh/copilot", tags=["mesh-copilot"])


@router.post("/generate", response_model=CopilotGenerateResponse)
async def post_copilot_generate(
    user: RequireAuth,
    db: DbSession,
    payload: CopilotGenerateRequest,
) -> CopilotGenerateResponse:
    try:
        return await generate_workflow_from_prompt(
            db,
            user,
            payload.prompt,
            payload.context_hints,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/explain", response_model=CopilotExplainResponse)
async def post_copilot_explain(
    user: RequireAuth,
    db: DbSession,
    payload: CopilotExplainRequest,
) -> CopilotExplainResponse:
    try:
        return await explain_workflow(db, user, payload.workflow_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/generate-workflow", response_model=CopilotGenerateWorkflowResponse)
async def post_generate_workflow(
    user: RequireAuth,
    redis: RedisDep,
    payload: CopilotGenerateWorkflowRequest,
) -> CopilotGenerateWorkflowResponse:
    generator = WorkflowGenerator.from_settings()
    draft = await generator.generate_from_nl(payload.prompt, user.tenant_id, payload.locale)
    await save_draft(redis, draft)
    return CopilotGenerateWorkflowResponse(draft=draft)


@router.post("/commit-workflow", response_model=CopilotCommitWorkflowResponse)
async def post_commit_workflow(
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
    payload: CopilotCommitWorkflowRequest,
) -> CopilotCommitWorkflowResponse:
    draft = await load_draft(redis, payload.draft_id)
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found or expired")
    if draft.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Draft tenant mismatch")
    definition = draft_to_mesh_definition(draft)
    created = await create_workflow(db, redis, user, definition)
    await db.commit()
    await delete_draft(redis, payload.draft_id)
    return CopilotCommitWorkflowResponse(workflow_id=created.id, name=created.name)


@router.get("/examples")
async def get_copilot_examples(
    _user: RequireAuth,
    locale: str | None = Query(default=None),
) -> list[CopilotExampleItem] | list[CopilotNlExampleItem]:
    if locale is not None:
        nl_items: list[CopilotNlExampleItem] = []
        for row in list_nl_examples(locale):
            draft_raw = row.get("draft")
            if not isinstance(draft_raw, dict):
                continue
            draft = WorkflowDraft.model_validate(draft_raw)
            nl_items.append(
                CopilotNlExampleItem(
                    prompt=str(row.get("prompt", "")),
                    prompt_id=str(row.get("prompt_id", "")),
                    prompt_en=str(row.get("prompt_en", "")),
                    draft=draft,
                )
            )
        return nl_items
    items: list[CopilotExampleItem] = []
    for row in list_examples():
        prompt = str(row["prompt"])
        wf_raw = row["workflow"]
        if isinstance(wf_raw, dict):
            items.append(
                CopilotExampleItem(prompt=prompt, workflow=MeshWorkflowDefinition.model_validate(wf_raw))
            )
    return items
