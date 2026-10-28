"""Convert WorkflowDraft (NL preview) into MeshWorkflowDefinition for persistence."""

from __future__ import annotations

import re

from app.mesh.ai_copilot.workflow_draft import DraftAction, DraftTriggerKind, WorkflowDraft
from app.mesh.workflow_schema import (
    DeviceResolverSpec,
    MeshWorkflowDefinition,
    WorkflowAction,
    WorkflowActionType,
    WorkflowTrigger,
    WorkflowTriggerFilter,
    WorkflowTriggerType,
)


def draft_to_mesh_definition(draft: WorkflowDraft) -> MeshWorkflowDefinition:
    trigger = _draft_trigger_to_mesh(draft)
    actions = [_draft_action_to_mesh(item, index) for index, item in enumerate(draft.actions)]
    slug = re.sub(r"[^a-z0-9]+", "-", draft.name.lower()).strip("-")[:48] or "copilot-workflow"
    return MeshWorkflowDefinition(
        name=slug,
        description=draft.description,
        enabled=True,
        trigger=trigger,
        conditions=[],
        actions=actions,
    )


def _draft_trigger_to_mesh(draft: WorkflowDraft) -> WorkflowTrigger:
    t = draft.trigger
    if t.kind == DraftTriggerKind.CRON:
        return WorkflowTrigger(
            type=WorkflowTriggerType.SCHEDULE,
            filter=WorkflowTriggerFilter(schedule_cron=t.cron or "0 6 * * *"),
        )
    if t.kind == DraftTriggerKind.EVENT:
        return WorkflowTrigger(
            type=WorkflowTriggerType.MESH_EVENT,
            filter=WorkflowTriggerFilter(
                domain=t.domain or "sensor",
                event_type=t.event_type or "threshold_exceeded",
            ),
        )
    metric = t.sensor or "soil_moisture"
    return WorkflowTrigger(
        type=WorkflowTriggerType.MESH_EVENT,
        filter=WorkflowTriggerFilter(
            domain="sensor",
            event_type="threshold_exceeded",
            payload_match={
                "metric": metric,
                "operator": t.operator or "lt",
                "threshold": t.threshold if t.threshold is not None else 40,
                "device_ref": t.device,
            },
        ),
    )


def _draft_action_to_mesh(action: DraftAction, index: int) -> WorkflowAction:
    action_id = f"action-{index + 1}"
    normalized = action.action.lower()
    if normalized in {"notify", "notification", "alert", "wa", "whatsapp"}:
        channels = action.channels or ["whatsapp"]
        return WorkflowAction(
            id=action_id,
            type=WorkflowActionType.NOTIFICATION,
            channels=channels,
            template=action.template or "Alert from Next-IOT copilot workflow.",
        )
    if normalized == "webhook":
        return WorkflowAction(
            id=action_id,
            type=WorkflowActionType.LOG_EVENT,
            log_message=f"Webhook: {action.webhook_url or 'configured'}",
        )
    if normalized in {"alarm", "create_alarm"}:
        return WorkflowAction(
            id=action_id,
            type=WorkflowActionType.CREATE_ALARM,
            alarm_type="sensor",
            severity=action.severity or "medium",
            title=action.template or "Sensor alert",
            message=action.template or "Threshold exceeded",
        )
    params: dict[str, object] = {}
    if action.duration_minutes is not None:
        params["duration_minutes"] = action.duration_minutes
    if action.duration_seconds is not None:
        params["duration_seconds"] = action.duration_seconds
    capability = "can_control_valve"
    command = "open_valve"
    if normalized in {"close", "shut"}:
        command = "close_valve"
    elif normalized in {"on", "turn_on", "nyalakan"}:
        command = "turn_on"
    elif normalized in {"off", "turn_off", "matikan"}:
        command = "turn_off"
    device_ref = action.actuator or "default_actuator"
    return WorkflowAction(
        id=action_id,
        type=WorkflowActionType.TRIGGER_DEVICE,
        device_resolver=DeviceResolverSpec(capability=capability, device_id=device_ref),
        command=command,
        params=params,
    )
