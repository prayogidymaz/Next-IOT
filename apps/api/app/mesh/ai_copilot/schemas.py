"""HTTP schemas for mesh AI copilot."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from app.mesh.workflow_schema import MeshWorkflowDefinition
from app.types.json_types import JsonObject


class CopilotGenerateRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=4000)
    context_hints: JsonObject = Field(default_factory=dict)


class CopilotGenerateResponse(BaseModel):
    workflow: MeshWorkflowDefinition
    explanation: str
    confidence: float


class CopilotExplainRequest(BaseModel):
    workflow_id: uuid.UUID


class CopilotExplainResponse(BaseModel):
    explanation: str
    flow_diagram: str


class CopilotExampleItem(BaseModel):
    prompt: str
    workflow: MeshWorkflowDefinition
