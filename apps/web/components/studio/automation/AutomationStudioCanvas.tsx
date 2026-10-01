"use client";

import {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
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
import { useCallback, useMemo, useRef, useState, type DragEvent } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import { deployAutomationPipeline } from "@/lib/api/automation";
import {
  INITIAL_EDGES,
  INITIAL_NODES,
  PALETTE_ITEMS,
  PIPELINE_DEPLOY_ID_KEY,
  WORKFLOW_STORAGE_KEY,
  createNodeFromPalette,
  type AutomationNodeData,
  type AutomationNodeKind,
  type AutomationWorkflowExport,
} from "@/lib/studio/automation-flow";

import { AutomationFlowNode } from "./AutomationFlowNode";
import { AutomationPropertyPanel } from "./AutomationPropertyPanel";

const nodeTypes = { automation: AutomationFlowNode };

const DND_MIME = "application/next-iot-automation-node";

function CanvasInner() {
  const { screenToFlowPosition } = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState<Node<AutomationNodeData>>(INITIAL_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>(INITIAL_EDGES);
  const [selectedId, setSelectedId] = useState<string | null>("trigger-1");
  const [status, setStatus] = useState<string | null>(null);
  const [deployState, setDeployState] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [deployMessage, setDeployMessage] = useState<string | null>(null);
  const importRef = useRef<HTMLInputElement>(null);

  const selectedNode = useMemo(
    () => nodes.find((n) => n.id === selectedId) ?? null,
    [nodes, selectedId],
  );

  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge({ ...connection, animated: true }, eds)),
    [setEdges],
  );

  const onPaletteDragStart = (e: DragEvent, kind: AutomationNodeKind, label: string) => {
    e.dataTransfer.setData(DND_MIME, JSON.stringify({ kind, label }));
    e.dataTransfer.effectAllowed = "move";
  };

  const onDragOver = (e: DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    const raw = e.dataTransfer.getData(DND_MIME);
    if (!raw) return;
    try {
      const { kind, label } = JSON.parse(raw) as { kind: AutomationNodeKind; label: string };
      const position = screenToFlowPosition({ x: e.clientX, y: e.clientY });
      const node = createNodeFromPalette(kind, label, position);
      setNodes((nds) => nds.concat(node));
      setSelectedId(node.id);
    } catch {
      /* ignore */
    }
  };

  const patchNode = (nodeId: string, patch: Partial<AutomationNodeData>) => {
    setNodes((nds) =>
      nds.map((n) => (n.id === nodeId ? { ...n, data: { ...n.data, ...patch } } : n)),
    );
  };

  const exportPayload = (): AutomationWorkflowExport => ({
    version: 1,
    name: "biofloc-heat-response",
    nodes,
    edges,
  });

  const saveWorkflow = () => {
    localStorage.setItem(WORKFLOW_STORAGE_KEY, JSON.stringify(exportPayload()));
    setStatus("Workflow saved locally.");
  };

  const exportJson = () => {
    const blob = new Blob([JSON.stringify(exportPayload(), null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "automation-workflow.json";
    a.click();
    URL.revokeObjectURL(url);
    setStatus("Exported automation-workflow.json");
  };

  const importJson = (file: File) => {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = JSON.parse(String(reader.result)) as AutomationWorkflowExport;
        if (!parsed.nodes || !parsed.edges) throw new Error("Invalid shape");
        setNodes(parsed.nodes);
        setEdges(parsed.edges);
        setSelectedId(parsed.nodes[0]?.id ?? null);
        setStatus(`Imported ${parsed.name ?? "workflow"}`);
      } catch {
        setStatus("Import failed — invalid JSON");
      }
    };
    reader.readAsText(file);
  };

  const deployRules = async () => {
    setDeployState("loading");
    setDeployMessage(null);
    try {
      const workflow = exportPayload();
      const existingId = localStorage.getItem(PIPELINE_DEPLOY_ID_KEY);
      const saved = await deployAutomationPipeline({
        workflow,
        pipelineId: existingId,
      });
      localStorage.setItem(PIPELINE_DEPLOY_ID_KEY, saved.id);
      setDeployState("success");
      setDeployMessage("Workflow successfully deployed to Edge Rule Engine!");
      setStatus(`Pipeline ${saved.id.slice(0, 8)}… synced`);
    } catch (err) {
      setDeployState("error");
      setDeployMessage(err instanceof Error ? err.message : "Deploy failed");
    }
  };

  return (
    <div className="grid gap-4 xl:grid-cols-[220px_1fr_280px]">
      <CreamCard className="p-4">
        <h2 className="text-sm font-semibold text-ink-primary">Node palette</h2>
        <p className="mt-1 text-xs text-ink-secondary">Drag onto canvas</p>
        <ul className="mt-4 space-y-2">
          {PALETTE_ITEMS.map((item) => (
            <li key={item.label}>
              <div
                draggable
                onDragStart={(e) => onPaletteDragStart(e, item.kind, item.label)}
                className="cursor-grab rounded-xl border border-cream-border bg-white px-3 py-2 active:cursor-grabbing"
              >
                <p className="text-sm font-medium capitalize text-ink-primary">{item.label}</p>
                <p className="text-xs text-ink-secondary">{item.hint}</p>
              </div>
            </li>
          ))}
        </ul>
      </CreamCard>

      <div className="flex min-h-[520px] flex-col gap-3">
        <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-cream-border bg-white px-3 py-2 shadow-sm">
          <button type="button" className="hq-btn-soft text-xs" onClick={saveWorkflow}>
            Save Workflow
          </button>
          <button type="button" className="hq-btn-soft text-xs" onClick={exportJson}>
            Export JSON
          </button>
          <button type="button" className="hq-btn-soft text-xs" onClick={() => importRef.current?.click()}>
            Import JSON
          </button>
          <input
            ref={importRef}
            type="file"
            accept="application/json,.json"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) importJson(file);
              e.target.value = "";
            }}
          />
          <button
            type="button"
            className="hq-btn-primary inline-flex items-center gap-2 text-xs disabled:opacity-60"
            onClick={() => void deployRules()}
            disabled={deployState === "loading"}
          >
            {deployState === "loading" ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : null}
            Deploy Rules
          </button>
          {status ? <span className="text-xs text-ink-secondary">{status}</span> : null}
        </div>
        {deployState === "success" && deployMessage ? (
          <div className="rounded-xl border border-accent-emerald/30 bg-accent-emerald-soft px-3 py-2 text-sm text-accent-emerald">
            {deployMessage}
          </div>
        ) : null}
        {deployState === "error" && deployMessage ? (
          <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{deployMessage}</div>
        ) : null}

        <div className="min-h-[480px] flex-1 overflow-hidden rounded-2xl border border-cream-border bg-cream-alt shadow-card">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            onNodeClick={(_, node) => setSelectedId(node.id)}
            onPaneClick={() => setSelectedId(null)}
            onDragOver={onDragOver}
            onDrop={onDrop}
            fitView
            proOptions={{ hideAttribution: true }}
          >
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#ECECE8" />
            <Controls className="!rounded-xl !border-cream-border !shadow-card" />
            <MiniMap
              className="!rounded-xl !border-cream-border"
              maskColor="rgba(249, 248, 246, 0.75)"
              nodeColor={(n) => {
                const kind = (n.data as AutomationNodeData)?.kind;
                if (kind === "trigger") return "#10B981";
                if (kind === "condition") return "#F59E0B";
                return "#4F46E5";
              }}
            />
          </ReactFlow>
        </div>
      </div>

      <AutomationPropertyPanel node={selectedNode} onChange={patchNode} />
    </div>
  );
}

export function AutomationStudioCanvas() {
  return (
    <ReactFlowProvider>
      <CanvasInner />
    </ReactFlowProvider>
  );
}
