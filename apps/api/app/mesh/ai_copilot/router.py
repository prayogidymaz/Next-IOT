"""Mesh AI Copilot HTTP API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.mesh.ai_copilot.examples import list_examples
from app.mesh.ai_copilot.schemas import (
    CopilotExampleItem,
    CopilotExplainRequest,
    CopilotExplainResponse,
    CopilotGenerateRequest,
    CopilotGenerateResponse,
)
from app.mesh.ai_copilot.service import explain_workflow, generate_workflow_from_prompt
from app.mesh.workflow_schema import MeshWorkflowDefinition

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


@router.get("/examples", response_model=list[CopilotExampleItem])
async def get_copilot_examples(_user: RequireAuth) -> list[CopilotExampleItem]:
    items: list[CopilotExampleItem] = []
    for row in list_examples():
        prompt = str(row["prompt"])
        wf_raw = row["workflow"]
        if isinstance(wf_raw, dict):
            items.append(
                CopilotExampleItem(prompt=prompt, workflow=MeshWorkflowDefinition.model_validate(wf_raw))
            )
    return items
