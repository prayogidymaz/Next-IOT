"""Workflow versioning API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.types.json_types import JsonObject


class WorkflowVersionView(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    version_number: int
    snapshot_json: JsonObject
    created_by: uuid.UUID | None
    created_at: datetime
    is_active: bool
    parent_version_id: uuid.UUID | None


class VersionDiffView(BaseModel):
    added_nodes: list[str] = Field(default_factory=list)
    removed_nodes: list[str] = Field(default_factory=list)
    modified_nodes: list[str] = Field(default_factory=list)
    added_edges: list[str] = Field(default_factory=list)
    removed_edges: list[str] = Field(default_factory=list)


class CreateVersionBody(BaseModel):
    notes: str = ""
