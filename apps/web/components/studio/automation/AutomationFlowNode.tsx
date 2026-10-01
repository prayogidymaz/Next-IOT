"use client";

import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";
import { Bell, GitBranch, Thermometer } from "lucide-react";
import { memo } from "react";

import type { AutomationNodeData } from "@/lib/studio/automation-flow";

const STYLE: Record<
  AutomationNodeData["kind"],
  { border: string; bg: string; icon: typeof Thermometer; iconClass: string }
> = {
  trigger: {
    border: "border-accent-emerald/40",
    bg: "bg-accent-emerald-soft/70",
    icon: Thermometer,
    iconClass: "text-accent-emerald",
  },
  condition: {
    border: "border-accent-amber/50",
    bg: "bg-accent-amber-soft/80",
    icon: GitBranch,
    iconClass: "text-accent-amber",
  },
  action: {
    border: "border-accent-indigo/40",
    bg: "bg-accent-indigo-soft/70",
    icon: Bell,
    iconClass: "text-accent-indigo",
  },
};

function AutomationFlowNodeComponent({ data, selected }: NodeProps<Node<AutomationNodeData>>) {
  const theme = STYLE[data.kind];
  const Icon = theme.icon;

  return (
    <div
      className={`min-w-[200px] rounded-2xl border-2 ${theme.border} ${theme.bg} px-4 py-3 shadow-card transition ${
        selected ? "ring-2 ring-accent-cobalt/40" : ""
      }`}
    >
      {data.kind !== "trigger" ? (
        <Handle type="target" position={Position.Left} className="!h-3 !w-3 !border-2 !border-white !bg-accent-cobalt" />
      ) : null}
      <div className="flex items-start gap-2">
        <span className={`rounded-lg bg-white/80 p-1.5 ${theme.iconClass}`}>
          <Icon className="h-4 w-4" />
        </span>
        <div className="min-w-0">
          <p className="text-[10px] font-bold uppercase tracking-wide text-ink-tertiary">{data.kind}</p>
          <p className="font-semibold text-ink-primary">{data.label}</p>
          {data.kind === "condition" && data.threshold !== undefined ? (
            <p className="text-xs text-ink-secondary">
              {data.operator ?? ">"} {data.threshold}°C
            </p>
          ) : null}
          {data.kind === "trigger" && data.sensorId ? (
            <p className="truncate font-mono text-[10px] text-ink-secondary">{data.sensorId}</p>
          ) : null}
        </div>
      </div>
      {data.kind !== "action" ? (
        <Handle type="source" position={Position.Right} className="!h-3 !w-3 !border-2 !border-white !bg-accent-cobalt" />
      ) : null}
    </div>
  );
}

export const AutomationFlowNode = memo(AutomationFlowNodeComponent);
