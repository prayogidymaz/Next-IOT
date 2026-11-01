"use client";

import { Background, Controls, ReactFlow, ReactFlowProvider } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

type WorkflowDefinitionPreview = {
  nodes?: { id: string; position?: { x: number; y: number }; data?: { label?: string } }[];
  edges?: unknown[];
  trigger?: { type?: string };
  conditions?: unknown[];
  actions?: { type?: string }[];
};

function hasVisualGraph(definition: WorkflowDefinitionPreview | undefined): boolean {
  return Boolean(definition?.nodes && definition.nodes.length > 0);
}

function buildSummary(definition: WorkflowDefinitionPreview | undefined): string[] {
  if (!definition) return [];
  const lines: string[] = [];
  const triggerType = definition.trigger?.type;
  if (triggerType) lines.push(`Trigger: ${triggerType}`);
  const condCount = definition.conditions?.length ?? 0;
  lines.push(`Conditions: ${condCount} condition(s)`);
  const actions = definition.actions ?? [];
  if (actions.length > 0) {
    lines.push(`Actions: ${actions.map((a) => a.type ?? "action").join(", ")}`);
  }
  return lines;
}

type Props = {
  snapshot: Record<string, unknown>;
  onDownload: () => void;
};

export function MarketplacePreviewPanel({ snapshot, onDownload }: Props) {
  const definition = snapshot.definition as WorkflowDefinitionPreview | undefined;

  if (!hasVisualGraph(definition)) {
    const summary = buildSummary(definition);
    return (
      <div className="rounded-xl border border-dashed border-stone-300 bg-stone-50 p-6 text-center">
        <p className="text-3xl" aria-hidden>
          🧩
        </p>
        <h2 className="mt-2 text-sm font-semibold text-stone-800">Preview tidak tersedia untuk template ini</h2>
        <p className="mt-1 text-xs text-stone-600">Struktur workflow akan terlihat setelah download</p>
        {summary.length > 0 ? (
          <ul className="mx-auto mt-4 max-w-sm space-y-1 text-left text-xs text-stone-700">
            {summary.map((line) => (
              <li key={line} className="rounded-md bg-white px-3 py-2 shadow-sm">
                {line}
              </li>
            ))}
          </ul>
        ) : null}
        <button
          type="button"
          className="mt-4 rounded-lg bg-stone-900 px-4 py-2 text-sm text-white"
          onClick={onDownload}
        >
          Download untuk Preview Lengkap
        </button>
      </div>
    );
  }

  const nodes =
    definition?.nodes?.map((n, i) => ({
      id: n.id,
      type: "default" as const,
      position: n.position ?? { x: i * 80, y: 40 },
      data: { label: n.data?.label ?? n.id },
    })) ?? [];

  return (
    <div className="h-48 rounded-lg border border-stone-200 bg-stone-50">
      <ReactFlowProvider>
        <ReactFlow nodes={nodes} edges={[]} fitView nodesDraggable={false} nodesConnectable={false} elementsSelectable={false}>
          <Background />
          <Controls showInteractive={false} />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}
