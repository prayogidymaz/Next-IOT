import type { Edge, Node } from "@xyflow/react";

export type AutomationNodeKind = "trigger" | "condition" | "action";

export type AutomationNodeData = {
  kind: AutomationNodeKind;
  label: string;
  sensorId?: string;
  operator?: ">" | "<" | "==" | "!=";
  threshold?: number;
  relayPin?: string;
  notifyMessage?: string;
};

export type AutomationWorkflowExport = {
  version: 1;
  name: string;
  nodes: Node<AutomationNodeData>[];
  edges: Edge[];
};

export const PALETTE_ITEMS: {
  kind: AutomationNodeKind;
  label: string;
  hint: string;
}[] = [
  { kind: "trigger", label: "Telemetry trigger", hint: "Sensor reading event" },
  { kind: "condition", label: "Threshold condition", hint: "Compare value / schedule" },
  { kind: "action", label: "Relay action", hint: "GPIO / relay output" },
  { kind: "action", label: "Notify action", hint: "WhatsApp / push alert" },
];

export const INITIAL_NODES: Node<AutomationNodeData>[] = [
  {
    id: "trigger-1",
    type: "automation",
    position: { x: 80, y: 120 },
    data: {
      kind: "trigger",
      label: "Biofloc temperature",
      sensorId: "pond-a/temp",
    },
  },
  {
    id: "condition-1",
    type: "automation",
    position: { x: 360, y: 120 },
    data: {
      kind: "condition",
      label: "Temp > 30°C",
      operator: ">",
      threshold: 30,
    },
  },
  {
    id: "action-1",
    type: "automation",
    position: { x: 640, y: 60 },
    data: {
      kind: "action",
      label: "Aerator ON",
      relayPin: "aerator-main/ch1",
    },
  },
  {
    id: "action-2",
    type: "automation",
    position: { x: 640, y: 200 },
    data: {
      kind: "action",
      label: "WhatsApp alert",
      notifyMessage: "Biofloc heat — aerator started",
    },
  },
];

export const INITIAL_EDGES: Edge[] = [
  { id: "e-t-c", source: "trigger-1", target: "condition-1", animated: true },
  { id: "e-c-a1", source: "condition-1", target: "action-1" },
  { id: "e-c-a2", source: "condition-1", target: "action-2" },
];

export function createNodeFromPalette(
  kind: AutomationNodeKind,
  label: string,
  position: { x: number; y: number },
): Node<AutomationNodeData> {
  const id = `${kind}-${crypto.randomUUID().slice(0, 8)}`;
  return {
    id,
    type: "automation",
    position,
    data: {
      kind,
      label,
      sensorId: kind === "trigger" ? "sensor/default" : undefined,
      operator: kind === "condition" ? ">" : undefined,
      threshold: kind === "condition" ? 30 : undefined,
      relayPin: kind === "action" && label.toLowerCase().includes("relay") ? "relay/1" : undefined,
      notifyMessage:
        kind === "action" && label.toLowerCase().includes("notify")
          ? "Alert from Automation Studio"
          : undefined,
    },
  };
}

export const WORKFLOW_STORAGE_KEY = "next-iot-automation-workflow";
export const PIPELINE_DEPLOY_ID_KEY = "next-iot-automation-pipeline-id";
