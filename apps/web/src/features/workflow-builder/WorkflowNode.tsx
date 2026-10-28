"use client";

import type { Node, NodeProps } from "@xyflow/react";

import type { WorkflowNodeData } from "./types";

export function WorkflowNode({ data }: NodeProps<Node<WorkflowNodeData>>) {
  return (
    <div className="min-w-[140px] rounded-lg border border-stone-300 bg-white px-3 py-2 shadow-sm">
      <div className="text-[10px] uppercase tracking-wide text-stone-500">{data.kind}</div>
      <div className="text-sm font-medium text-stone-900">{data.label}</div>
    </div>
  );
}
