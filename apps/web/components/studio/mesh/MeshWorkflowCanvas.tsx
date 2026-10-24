"use client";

import {
  Background,
  BackgroundVariant,
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
import { Loader2 } from "lucide-react";
import { useCallback, useMemo, useState, type DragEvent } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import { createMeshWorkflow, listMeshWorkflowExecutions, testMeshWorkflow } from "@/lib/api/mesh";
import {
  INITIAL_MESH_EDGES,
  INITIAL_MESH_NODES,
  MESH_PALETTE_ITEMS,
  createMeshNodeFromPalette,
  meshNodesToDefinition,
  type MeshWorkflowNodeData,
  type MeshWorkflowNodeKind,
} from "@/lib/studio/mesh-workflow-flow";

import { MeshWorkflowFlowNode } from "./MeshWorkflowFlowNode";
import { MeshWorkflowPropertyPanel } from "./MeshWorkflowPropertyPanel";

const nodeTypes = { meshWorkflow: MeshWorkflowFlowNode };
const DND_MIME = "application/next-iot-mesh-workflow-node";

function CanvasInner() {
  const { screenToFlowPosition } = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState<Node<MeshWorkflowNodeData>>(INITIAL_MESH_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>(INITIAL_MESH_EDGES);
  const [selectedId, setSelectedId] = useState<string | null>("mesh-trigger-1");
  const [workflowName, setWorkflowName] = useState("mesh-cross-domain-demo");
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [deployState, setDeployState] = useState<"idle" | "loading">("idle");
  const [executions, setExecutions] = useState<string[]>([]);

  const selectedNode = useMemo(
    () => nodes.find((n) => n.id === selectedId) ?? null,
    [nodes, selectedId],
  );

  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge({ ...connection, animated: true }, eds)),
    [setEdges],
  );

  const onPaletteDragStart = (e: DragEvent, kind: MeshWorkflowNodeKind, label: string) => {
    e.dataTransfer.setData(DND_MIME, JSON.stringify({ kind, label }));
    e.dataTransfer.effectAllowed = "move";
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    const raw = e.dataTransfer.getData(DND_MIME);
    if (!raw) return;
    try {
      const { kind, label } = JSON.parse(raw) as { kind: MeshWorkflowNodeKind; label: string };
      const position = screenToFlowPosition({ x: e.clientX, y: e.clientY });
      const node = createMeshNodeFromPalette(kind, label, position);
      setNodes((nds) => nds.concat(node));
      setSelectedId(node.id);
    } catch {
      /* ignore invalid drag payload */
    }
  };

  const patchNode = (nodeId: string, patch: Partial<MeshWorkflowNodeData>) => {
    setNodes((nds) =>
      nds.map((n) => (n.id === nodeId ? { ...n, data: { ...n.data, ...patch } } : n)),
    );
  };

  const deploy = async () => {
    setDeployState("loading");
    setStatus(null);
    try {
      const definition = meshNodesToDefinition(nodes, workflowName);
      const saved = await createMeshWorkflow(definition);
      setWorkflowId(saved.id);
      setStatus(`Deployed workflow ${saved.id.slice(0, 8)}…`);
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Deploy failed");
    } finally {
      setDeployState("idle");
    }
  };

  const runTest = async () => {
    if (!workflowId) {
      setStatus("Deploy workflow terlebih dahulu.");
      return;
    }
    try {
      const sample = {
        domain: "vision",
        event_type: "motion_detected",
        payload: { confidence: 0.9 },
      };
      const dry = await testMeshWorkflow(workflowId, sample);
      setStatus(
        dry.conditions_passed
          ? `Dry-run OK — ${dry.planned_actions.length} planned actions`
          : `Skipped: ${dry.skipped_reason ?? "conditions"}`,
      );
      const logs = await listMeshWorkflowExecutions(workflowId);
      setExecutions(logs.slice(0, 5).map((l) => `${l.status} · ${l.started_at}`));
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Test failed");
    }
  };

  return (
    <div className="grid gap-4 xl:grid-cols-[220px_1fr_280px]">
      <CreamCard className="p-4">
        <h2 className="text-sm font-semibold text-ink-primary">Mesh palette</h2>
        <ul className="mt-4 space-y-2">
          {MESH_PALETTE_ITEMS.map((item) => (
            <li key={item.label}>
              <div
                draggable
                onDragStart={(e) => onPaletteDragStart(e, item.kind, item.label)}
                className="cursor-grab rounded-xl border border-cream-border bg-white px-3 py-2"
              >
                <p className="text-sm font-medium text-ink-primary">{item.label}</p>
                <p className="text-xs text-ink-secondary">{item.hint}</p>
              </div>
            </li>
          ))}
        </ul>
      </CreamCard>

      <div className="flex min-h-[480px] flex-col gap-3">
        <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-cream-border bg-white px-3 py-2">
          <input
            className="rounded-lg border border-cream-border px-2 py-1 text-xs"
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            aria-label="Workflow name"
          />
          <button
            type="button"
            className="hq-btn-primary inline-flex items-center gap-2 text-xs disabled:opacity-60"
            disabled={deployState === "loading"}
            onClick={() => void deploy()}
          >
            {deployState === "loading" ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : null}
            Deploy Mesh Workflow
          </button>
          <button type="button" className="hq-btn-soft text-xs" onClick={() => void runTest()}>
            Test
          </button>
          {status ? <span className="text-xs text-ink-secondary">{status}</span> : null}
        </div>
        <div
          className="min-h-[420px] flex-1 overflow-hidden rounded-2xl border border-cream-border bg-cream-alt"
          onDragOver={(e) => e.preventDefault()}
          onDrop={onDrop}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            onNodeClick={(_, node) => setSelectedId(node.id)}
            fitView
            proOptions={{ hideAttribution: true }}
          >
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#ECECE8" />
            <Controls className="!rounded-xl !border-cream-border" />
          </ReactFlow>
        </div>
        {executions.length > 0 ? (
          <div className="rounded-xl border border-cream-border bg-white p-3 text-xs text-ink-secondary">
            <p className="font-semibold text-ink-primary">Recent executions</p>
            <ul className="mt-2 list-disc pl-4">
              {executions.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>

      <MeshWorkflowPropertyPanel node={selectedNode} onChange={patchNode} />
    </div>
  );
}

export function MeshWorkflowCanvas() {
  return (
    <ReactFlowProvider>
      <CanvasInner />
    </ReactFlowProvider>
  );
}
