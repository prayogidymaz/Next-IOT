"""Parse LLM output into validated MeshWorkflowDefinition."""

from __future__ import annotations

import json
import re
import uuid

from app.mesh.workflow_schema import MeshWorkflowDefinition
from app.types.json_types import JsonObject


def _strip_code_fence(raw: str) -> str:
    text = raw.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text


def parse_llm_workflow_payload(raw: str | JsonObject) -> MeshWorkflowDefinition:
    if isinstance(raw, dict):
        return MeshWorkflowDefinition.model_validate(raw)
    text = _strip_code_fence(raw)
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("LLM workflow must be a JSON object")
    return MeshWorkflowDefinition.model_validate(data)


def enrich_workflow_context(
    definition: MeshWorkflowDefinition,
    *,
    tenant_id: uuid.UUID,
    context: JsonObject,
) -> MeshWorkflowDefinition:
    """Attach tenant-scoped hints into description (non-destructive)."""
    hints: list[str] = []
    farm_id = context.get("farm_id")
    if isinstance(farm_id, str) and farm_id.strip():
        hints.append(f"farm_id={farm_id}")
    device_types = context.get("device_types")
    if isinstance(device_types, list) and device_types:
        hints.append("devices=" + ",".join(str(x) for x in device_types))
    hints.append(f"tenant_id={tenant_id}")
    if not hints:
        return definition
    suffix = " [" + "; ".join(hints) + "]"
    if suffix in definition.description:
        return definition
    return definition.model_copy(update={"description": definition.description + suffix})
