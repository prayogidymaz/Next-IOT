import type { Edge, Node } from "@xyflow/react";

export type MeshWorkflowNodeKind =
  | "mesh_event"
  | "dispatch_device"
  | "wait_for_event"
  | "device_resolver";

export type MeshWorkflowNodeData = {
  kind: MeshWorkflowNodeKind;
  label: string;
  domain?: string;
  eventType?: string;
  capability?: string;
  zone?: string;
  command?: string;
  waitDomain?: string;
  waitEventType?: string;
  configJson?: string;
};

export const MESH_PALETTE_ITEMS: { kind: MeshWorkflowNodeKind; label: string; hint: string }[] = [
  { kind: "mesh_event", label: "Mesh event trigger", hint: "domain + event_type filter" },
  { kind: "device_resolver", label: "Device resolver", hint: "capability / zone selector" },
  { kind: "dispatch_device", label: "Dispatch device", hint: "command + params" },
  { kind: "wait_for_event", label: "Wait for event", hint: "correlation wait step" },
];

export const INITIAL_MESH_NODES: Node<MeshWorkflowNodeData>[] = [
  {
    id: "mesh-trigger-1",
    type: "meshWorkflow",
    position: { x: 60, y: 140 },
    data: { kind: "mesh_event", label: "motion_detected", domain: "vision", eventType: "motion_detected" },
  },
  {
    id: "mesh-resolver-1",
    type: "meshWorkflow",
    position: { x: 300, y: 140 },
    data: { kind: "device_resolver", label: "Nearest sprayer", capability: "irrigation_valve", zone: "plot_A" },
  },
  {
    id: "mesh-action-1",
    type: "meshWorkflow",
    position: { x: 540, y: 140 },
    data: { kind: "dispatch_device", label: "Open valve", command: "SET_ACTUATOR", configJson: "{\"value\":\"open_valve\"}" },
  },
];

export const INITIAL_MESH_EDGES: Edge[] = [
  { id: "m-e1", source: "mesh-trigger-1", target: "mesh-resolver-1", animated: true },
  { id: "m-e2", source: "mesh-resolver-1", target: "mesh-action-1", animated: true },
];

export function createMeshNodeFromPalette(
  kind: MeshWorkflowNodeKind,
  label: string,
  position: { x: number; y: number },
): Node<MeshWorkflowNodeData> {
  const id = `mesh-${kind}-${crypto.randomUUID().slice(0, 8)}`;
  return {
    id,
    type: "meshWorkflow",
    position,
    data: {
      kind,
      label,
      domain: kind === "mesh_event" ? "vision" : undefined,
      eventType: kind === "mesh_event" ? "motion_detected" : undefined,
      capability: kind === "device_resolver" ? "irrigation_valve" : undefined,
      command: kind === "dispatch_device" ? "SET_ACTUATOR" : undefined,
      waitDomain: kind === "wait_for_event" ? "actuator" : undefined,
      waitEventType: kind === "wait_for_event" ? "state_changed" : undefined,
      configJson: "{}",
    },
  };
}

export function meshNodesToDefinition(
  nodes: Node<MeshWorkflowNodeData>[],
  name: string,
): {
  name: string;
  description: string;
  enabled: boolean;
  trigger: { type: "mesh_event"; filter: { domain: string | null; event_type: string | null } };
  conditions: Record<string, unknown>[];
  actions: Record<string, unknown>[];
} {
  const triggerNode = nodes.find((n) => n.data.kind === "mesh_event");
  const actions = nodes
    .filter((n) => n.data.kind === "dispatch_device" || n.data.kind === "wait_for_event")
    .map((n, index) => {
      if (n.data.kind === "wait_for_event") {
        return {
          id: `wait-${index + 1}`,
          type: "wait_for_event",
          wait_for: {
            domain: n.data.waitDomain ?? "actuator",
            event_type: n.data.waitEventType ?? "state_changed",
          },
        };
      }
      let params: Record<string, unknown> = {};
      if (n.data.configJson) {
        try {
          const parsed: unknown = JSON.parse(n.data.configJson);
          if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
            params = parsed as Record<string, unknown>;
          }
        } catch {
          params = {};
        }
      }
      const resolverNode = nodes.find((x) => x.data.kind === "device_resolver");
      return {
        id: `action-${index + 1}`,
        type: "dispatch_device",
        command: n.data.command ?? "SET_ACTUATOR",
        params,
        device_resolver: {
          capability: resolverNode?.data.capability ?? "irrigation_valve",
          zone: resolverNode?.data.zone ?? null,
        },
      };
    });

  return {
    name,
    description: "Mesh workflow from Automation Studio",
    enabled: true,
    trigger: {
      type: "mesh_event",
      filter: {
        domain: triggerNode?.data.domain ?? null,
        event_type: triggerNode?.data.eventType ?? null,
      },
    },
    conditions: [],
    actions,
  };
}
