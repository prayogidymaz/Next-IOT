import type { Edge, Node } from "@xyflow/react";

import type { WorkflowDraft, WorkflowNodeData } from "./types";

export function draftToFlow(draft: WorkflowDraft): { nodes: Node<WorkflowNodeData>[]; edges: Edge[] } {
  const triggerId = "trigger-1";
  const nodes: Node<WorkflowNodeData>[] = [
    {
      id: triggerId,
      type: "workflowNode",
      position: { x: 80, y: 120 },
      data: {
        kind: "trigger",
        label: draft.name,
        triggerKind: draft.trigger.kind,
        sensor: draft.trigger.sensor,
        operator: draft.trigger.operator,
        threshold: draft.trigger.threshold,
        cron: draft.trigger.cron,
      },
    },
  ];
  const edges: Edge[] = [];
  draft.actions.forEach((action, index) => {
    const id = `action-${index + 1}`;
    nodes.push({
      id,
      type: "workflowNode",
      position: { x: 360, y: 80 + index * 100 },
      data: {
        kind: "action",
        label: action.action,
        action: action.action,
        actuator: action.actuator,
        duration_minutes: action.duration_minutes,
      },
    });
    edges.push({ id: `e-${index}`, source: triggerId, target: id, animated: true });
  });
  return { nodes, edges };
}

export function flowToDefinitionPayload(
  nodes: Node<WorkflowNodeData>[],
  edges: Edge[],
  name: string,
): Record<string, unknown> {
  const trigger = nodes.find((n) => n.data.kind === "trigger");
  const actions = nodes.filter((n) => n.data.kind === "action");
  return {
    name,
    description: "Visual workflow builder export",
    enabled: true,
    trigger: {
      type: trigger?.data.triggerKind === "cron" ? "schedule" : "mesh_event",
      filter:
        trigger?.data.triggerKind === "cron"
          ? { schedule_cron: trigger.data.cron ?? "0 6 * * *" }
          : {
              domain: "sensor",
              event_type: "threshold_exceeded",
              payload_match: {
                metric: trigger?.data.sensor ?? "soil_moisture",
                operator: trigger?.data.operator ?? "lt",
                threshold: trigger?.data.threshold ?? 40,
              },
            },
    },
    conditions: nodes
      .filter((n) => n.data.kind === "condition")
      .map((n) => ({ type: n.data.logic ?? "and", label: n.data.label })),
    actions: actions.map((n, i) => ({
      id: `action-${i + 1}`,
      type: "trigger_device",
      command: n.data.action ?? "open_valve",
      device_resolver: { capability: "can_control_valve", device_id: n.data.actuator ?? "valve_A1" },
      params: { duration_minutes: n.data.duration_minutes ?? 15 },
    })),
    edges: edges.map((e) => ({ source: e.source, target: e.target })),
  };
}
