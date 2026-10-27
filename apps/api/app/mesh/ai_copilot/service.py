"""Mesh AI copilot orchestration."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.mesh.ai_copilot.client import LLMClient
from app.mesh.ai_copilot.parser import enrich_workflow_context, parse_llm_workflow_payload
from app.mesh.ai_copilot.schemas import CopilotExplainResponse, CopilotGenerateResponse
from app.mesh.workflow_registry import definition_from_row
from app.mesh.workflow_schema import MeshWorkflowDefinition
from app.models.mesh_workflow import MeshWorkflow


async def generate_workflow_from_prompt(
    _db: AsyncSession,
    user: CurrentUser,
    prompt: str,
    context_hints: dict[str, object],
) -> CopilotGenerateResponse:
    tenant_id = user.tenant_id
    client = LLMClient.from_settings()
    raw = await client.generate_workflow(prompt, context_hints)
    wf_raw = raw.get("workflow")
    if isinstance(wf_raw, str):
        definition = parse_llm_workflow_payload(wf_raw)
    elif isinstance(wf_raw, dict):
        definition = parse_llm_workflow_payload(wf_raw)
    else:
        raise ValueError("LLM response missing workflow")
    definition = enrich_workflow_context(definition, tenant_id=tenant_id, context=context_hints)
    explanation = str(raw.get("explanation", ""))
    confidence_raw = raw.get("confidence", 0.8)
    confidence = float(confidence_raw) if isinstance(confidence_raw, int | float) else 0.8
    return CopilotGenerateResponse(workflow=definition, explanation=explanation, confidence=confidence)


def _workflow_to_mermaid(definition: MeshWorkflowDefinition) -> str:
    lines = ["flowchart TD", f"  T[Trigger: {definition.trigger.type.value}]"]
    for idx, action in enumerate(definition.actions):
        lines.append(f"  T --> A{idx}[{action.type.value}: {action.id}]")
    return "\n".join(lines)


async def explain_workflow(
    db: AsyncSession,
    user: CurrentUser,
    workflow_id: uuid.UUID,
) -> CopilotExplainResponse:
    row = await db.scalar(select(MeshWorkflow).where(MeshWorkflow.id == workflow_id))
    if row is None:
        raise ValueError("workflow not found")
    if not user.is_super_admin and row.tenant_id != user.tenant_id:
        raise ValueError("workflow not found")
    definition = definition_from_row(row)
    explanation = (
        f"Workflow '{row.name}' has trigger {definition.trigger.type.value} "
        f"and {len(definition.actions)} action(s)."
    )
    return CopilotExplainResponse(explanation=explanation, flow_diagram=_workflow_to_mermaid(definition))
