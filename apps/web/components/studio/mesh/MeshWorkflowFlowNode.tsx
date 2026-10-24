"use client";

import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";

import type { MeshWorkflowNodeData } from "@/lib/studio/mesh-workflow-flow";

export function MeshWorkflowFlowNode({ data }: NodeProps<Node<MeshWorkflowNodeData>>) {
  const accent =
    data.kind === "mesh_event"
      ? "border-orange-300 bg-orange-50"
      : data.kind === "device_resolver"
        ? "border-indigo-300 bg-indigo-50"
        : data.kind === "wait_for_event"
          ? "border-amber-300 bg-amber-50"
          : "border-emerald-300 bg-emerald-50";

  return (
    <div className={`min-w-[140px] rounded-xl border-2 px-3 py-2 shadow-sm ${accent}`}>
      <Handle type="target" position={Position.Left} />
      <p className="text-[10px] uppercase text-ink-secondary">{data.kind.replace(/_/g, " ")}</p>
      <p className="text-sm font-semibold text-ink-primary">{data.label}</p>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
