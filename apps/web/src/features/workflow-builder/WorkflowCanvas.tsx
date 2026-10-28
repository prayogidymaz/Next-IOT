"use client";

import {
  Background,
  Controls,
  ReactFlow,
  ReactFlowProvider,
  addEdge,
  useEdgesState,
  useNodesState,
  useReactFlow,
  type Connection,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useCallback, useMemo, useState, type DragEvent } from "react";
import { FormProvider, useForm } from "react-hook-form";

import { CopilotBridge } from "./CopilotBridge";
import { DND_MIME, NodePalette } from "./NodePalette";
import { NodeInspector } from "./NodeInspector";
import { flowToDefinitionPayload } from "./serializer";
import type { WorkflowNodeData } from "./types";
import { WorkflowNode } from "./WorkflowNode";

const nodeTypes = { workflowNode: WorkflowNode };

const INITIAL_NODES: Node<WorkflowNodeData>[] = [
  {
    id: "trigger-1",
    type: "workflowNode",
    position: { x: 80, y: 140 },
    data: { kind: "trigger", label: "New trigger", triggerKind: "sensor_threshold", sensor: "soil_moisture" },
  },
];

type FormValues = { selectedNode: WorkflowNodeData | null };

type Props = {
  apiBase: string;
  token: string;
  workflowId?: string;
  initialNodes?: Node<WorkflowNodeData>[];
  initialEdges?: Edge[];
};

function CanvasInner({ apiBase, token, workflowId }: Props) {
  const { screenToFlowPosition, fitView } = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState<Node<WorkflowNodeData>>(INITIAL_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [selectedId, setSelectedId] = useState<string | null>("trigger-1");
  const [name, setName] = useState("workflow-visual");
  const [status, setStatus] = useState<string | null>(null);

  const form = useForm<FormValues>({
    defaultValues: { selectedNode: INITIAL_NODES[0]?.data ?? null },
  });

  const selectedNode = useMemo(() => nodes.find((n) => n.id === selectedId) ?? null, [nodes, selectedId]);

  const onConnect = useCallback(
    (connection: Connection) => {
      const source = nodes.find((n) => n.id === connection.source);
      const target = nodes.find((n) => n.id === connection.target);
      if (!source || !target) return;
      const valid =
        (source.data.kind === "trigger" && (target.data.kind === "condition" || target.data.kind === "action")) ||
        (source.data.kind === "condition" && target.data.kind === "action");
      if (!valid) {
        setStatus("Invalid edge: trigger → condition? → action");
        return;
      }
      setEdges((eds) => addEdge({ ...connection, animated: true }, eds));
    },
    [nodes, setEdges],
  );

  const onPaletteDragStart = (e: DragEvent, template: Partial<WorkflowNodeData>) => {
    e.dataTransfer.setData(DND_MIME, JSON.stringify(template));
    e.dataTransfer.effectAllowed = "move";
  };

  const onDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      const raw = e.dataTransfer.getData(DND_MIME);
      if (!raw) return;
      const template = JSON.parse(raw) as Partial<WorkflowNodeData>;
      const position = screenToFlowPosition({ x: e.clientX, y: e.clientY });
      const id = `${template.kind}-${crypto.randomUUID().slice(0, 8)}`;
      setNodes((nds) => [
        ...nds,
        {
          id,
          type: "workflowNode",
          position,
          data: {
            kind: template.kind ?? "action",
            label: template.label ?? "Node",
            ...template,
          } as WorkflowNodeData,
        },
      ]);
    },
    [screenToFlowPosition, setNodes],
  );

  const duplicateSelected = () => {
    if (!selectedNode) return;
    const copyId = `${selectedNode.id}-copy`;
    setNodes((nds) => [
      ...nds,
      {
        ...selectedNode,
        id: copyId,
        position: { x: selectedNode.position.x + 40, y: selectedNode.position.y + 40 },
      },
    ]);
  };

  const deleteSelected = () => {
    if (!selectedId) return;
    setNodes((nds) => nds.filter((n) => n.id !== selectedId));
    setEdges((eds) => eds.filter((e) => e.source !== selectedId && e.target !== selectedId));
    setSelectedId(null);
  };

  async function saveWorkflow() {
    const payload = flowToDefinitionPayload(nodes, edges, name);
    const url = workflowId
      ? `${apiBase}/api/v1/mesh/workflows/${workflowId}`
      : `${apiBase}/api/v1/mesh/workflows`;
    const resp = await fetch(url, {
      method: workflowId ? "PUT" : "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(payload),
    });
    setStatus(resp.ok ? "Saved" : `Save failed (${resp.status})`);
  }

  return (
    <FormProvider {...form}>
      <div className="flex h-[min(720px,80vh)] flex-col rounded-xl border border-stone-200 bg-stone-50">
        <div className="flex items-center gap-2 border-b border-stone-200 px-3 py-2">
          <input
            className="rounded border px-2 py-1 text-sm"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <button type="button" className="rounded border px-2 py-1 text-sm" onClick={() => setNodes((n) => [...n])}>
            Add node
          </button>
          <button type="button" className="rounded border px-2 py-1 text-sm" onClick={duplicateSelected}>
            Duplicate
          </button>
          <button type="button" className="rounded border px-2 py-1 text-sm" onClick={deleteSelected}>
            Delete
          </button>
          <button type="button" className="rounded border px-2 py-1 text-sm" onClick={() => fitView()}>
            Zoom fit
          </button>
          <button type="button" className="rounded bg-stone-900 px-2 py-1 text-sm text-white" onClick={() => void saveWorkflow()}>
            Save
          </button>
          <CopilotBridge
            apiBase={apiBase}
            token={token}
            onApply={(n, e) => {
              setNodes(n);
              setEdges(e);
              setSelectedId(n[0]?.id ?? null);
            }}
          />
          {status ? <span className="text-xs text-stone-600">{status}</span> : null}
        </div>
        <div className="flex min-h-0 flex-1">
          <NodePalette onDragStart={onPaletteDragStart} />
          <div className="relative min-w-0 flex-1" onDragOver={(e) => e.preventDefault()} onDrop={onDrop}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              nodeTypes={nodeTypes}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={(_, node) => {
                setSelectedId(node.id);
                form.setValue("selectedNode", node.data);
              }}
              fitView
            >
              <Background />
              <Controls />
            </ReactFlow>
          </div>
          <NodeInspector />
        </div>
      </div>
    </FormProvider>
  );
}

export function WorkflowCanvas(props: Props) {
  return (
    <ReactFlowProvider>
      <CanvasInner {...props} />
    </ReactFlowProvider>
  );
}
