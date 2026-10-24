"""Mesh workflow DSL (cross-domain orchestration)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.types.json_types import JsonObject, JsonValue


class WorkflowTriggerType(StrEnum):
    MESH_EVENT = "mesh_event"
    SCHEDULE = "schedule"
    MANUAL = "manual"


class WorkflowActionType(StrEnum):
    DISPATCH_DEVICE = "dispatch_device"
    TRIGGER_DEVICE = "trigger_device"
    WAIT_FOR_EVENT = "wait_for_event"
    NOTIFICATION = "notification"
    SET_ATTRIBUTE = "set_attribute"
    CREATE_ALARM = "create_alarm"
    LOG_EVENT = "log_event"


class WorkflowExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED_CONDITION = "skipped_condition"


class DeviceResolverSpec(BaseModel):
    capability: str | None = None
    zone: str | None = None
    farm_id: uuid.UUID | None = None
    plot_id: uuid.UUID | None = None
    nearest_to: JsonObject | str | None = None
    device_id: uuid.UUID | str | None = None
    state_match: JsonObject | None = None

    @model_validator(mode="after")
    def _require_selector(self) -> Self:
        if self.device_id is None and (self.capability is None or not self.capability.strip()):
            raise ValueError("device_resolver requires capability or device_id")
        return self


class WorkflowTriggerFilter(BaseModel):
    domain: str | None = None
    event_type: str | None = None
    payload_match: JsonObject | None = None
    context_match: JsonObject | None = None
    time_filter: JsonObject | None = None
    schedule_cron: str | None = None


class WorkflowTrigger(BaseModel):
    type: WorkflowTriggerType
    filter: WorkflowTriggerFilter | None = None


class WorkflowCondition(BaseModel):
    type: str
    device_resolver: DeviceResolverSpec | None = None
    state_match: JsonObject | None = None
    attribute: str | None = None


class WorkflowWaitForSpec(BaseModel):
    domain: str
    event_type: str
    from_device: str | None = None
    payload_match: JsonObject | None = None


class WorkflowAction(BaseModel):
    id: str
    type: WorkflowActionType
    device_resolver: DeviceResolverSpec | None = None
    command: str | None = None
    params: JsonObject = Field(default_factory=dict)
    wait_for: WorkflowWaitForSpec | None = None
    timeout_seconds: int | None = None
    channels: list[str] = Field(default_factory=list)
    template: str | None = None
    scope: str | None = None
    key: str | None = None
    value: JsonValue | None = None
    alarm_type: str | None = None
    severity: str | None = None
    title: str | None = None
    message: str | None = None
    log_message: str | None = None

    @model_validator(mode="after")
    def _validate_by_type(self) -> Self:
        if self.type in {WorkflowActionType.DISPATCH_DEVICE, WorkflowActionType.TRIGGER_DEVICE}:
            if not self.command:
                raise ValueError(f"{self.type} requires command")
            if self.device_resolver is None:
                raise ValueError(f"{self.type} requires device_resolver")
        if self.type == WorkflowActionType.WAIT_FOR_EVENT and self.wait_for is None:
            raise ValueError("wait_for_event requires wait_for")
        if self.type == WorkflowActionType.NOTIFICATION and not self.template:
            raise ValueError("notification requires template")
        if self.type == WorkflowActionType.SET_ATTRIBUTE:
            if not self.key or self.scope is None:
                raise ValueError("set_attribute requires scope and key")
        if self.type == WorkflowActionType.CREATE_ALARM and not self.title:
            raise ValueError("create_alarm requires title")
        if self.type == WorkflowActionType.LOG_EVENT and not self.log_message:
            raise ValueError("log_event requires log_message")
        return self


class MeshWorkflowDefinition(BaseModel):
    name: str
    description: str = ""
    enabled: bool = True
    trigger: WorkflowTrigger
    conditions: list[WorkflowCondition] = Field(default_factory=list)
    actions: list[WorkflowAction] = Field(default_factory=list)


class MeshWorkflowRecordView(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str
    enabled: bool
    definition: MeshWorkflowDefinition
    created_at: datetime
    updated_at: datetime


class WorkflowExecutionResult(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    tenant_id: uuid.UUID
    trigger_event_id: uuid.UUID | None
    status: WorkflowExecutionStatus
    started_at: datetime
    completed_at: datetime | None
    duration_ms: int | None
    action_results: JsonObject
    error_message: str | None
    correlation_id: uuid.UUID | None


class WorkflowDryRunRequest(BaseModel):
    sample_event: JsonObject


class WorkflowDryRunResponse(BaseModel):
    conditions_passed: bool
    planned_actions: list[JsonObject]
    skipped_reason: str | None = None
