"use client";

import type { Node } from "@xyflow/react";

import { CreamCard } from "@/components/ui/CreamCard";
import type { AutomationNodeData } from "@/lib/studio/automation-flow";

type AutomationPropertyPanelProps = {
  node: Node<AutomationNodeData> | null;
  onChange: (nodeId: string, patch: Partial<AutomationNodeData>) => void;
};

export function AutomationPropertyPanel({ node, onChange }: AutomationPropertyPanelProps) {
  if (!node) {
    return (
      <CreamCard className="flex h-full min-h-[420px] items-center justify-center p-6 text-center">
        <p className="text-sm text-ink-secondary">Select a node to configure thresholds, relay pins, or notifications.</p>
      </CreamCard>
    );
  }

  const { data } = node;

  return (
    <CreamCard className="flex h-full min-h-[420px] flex-col p-5">
      <h2 className="text-sm font-semibold text-ink-primary">Property configurator</h2>
      <p className="mt-1 text-xs text-ink-secondary capitalize">{data.kind} · {node.id}</p>

      <label className="mt-5 block text-sm">
        <span className="text-ink-secondary">Label</span>
        <input
          value={data.label}
          onChange={(e) => onChange(node.id, { label: e.target.value })}
          className="mt-1 w-full rounded-xl border border-cream-border bg-white px-3 py-2 text-sm"
        />
      </label>

      {data.kind === "trigger" ? (
        <label className="mt-4 block text-sm">
          <span className="text-ink-secondary">Sensor ID</span>
          <input
            value={data.sensorId ?? ""}
            onChange={(e) => onChange(node.id, { sensorId: e.target.value })}
            className="mt-1 w-full rounded-xl border border-cream-border bg-white px-3 py-2 font-mono text-xs"
            placeholder="pond-a/temp"
          />
        </label>
      ) : null}

      {data.kind === "condition" ? (
        <>
          <label className="mt-4 block text-sm">
            <span className="text-ink-secondary">Operator</span>
            <select
              value={data.operator ?? ">"}
              onChange={(e) => onChange(node.id, { operator: e.target.value as AutomationNodeData["operator"] })}
              className="mt-1 w-full rounded-xl border border-cream-border bg-white px-3 py-2 text-sm"
            >
              <option value=">">&gt;</option>
              <option value="<">&lt;</option>
              <option value="==">==</option>
              <option value="!=">!=</option>
            </select>
          </label>
          <label className="mt-4 block text-sm">
            <span className="text-ink-secondary">Threshold (°C)</span>
            <input
              type="number"
              value={data.threshold ?? 30}
              onChange={(e) => onChange(node.id, { threshold: Number(e.target.value) })}
              className="mt-1 w-full rounded-xl border border-cream-border bg-white px-3 py-2 text-sm"
            />
          </label>
        </>
      ) : null}

      {data.kind === "action" ? (
        <>
          <label className="mt-4 block text-sm">
            <span className="text-ink-secondary">Relay pin / channel</span>
            <input
              value={data.relayPin ?? ""}
              onChange={(e) => onChange(node.id, { relayPin: e.target.value })}
              className="mt-1 w-full rounded-xl border border-cream-border bg-white px-3 py-2 font-mono text-xs"
              placeholder="aerator-main/ch1"
            />
          </label>
          <label className="mt-4 block text-sm">
            <span className="text-ink-secondary">Notification message</span>
            <textarea
              value={data.notifyMessage ?? ""}
              onChange={(e) => onChange(node.id, { notifyMessage: e.target.value })}
              rows={4}
              className="mt-1 w-full rounded-xl border border-cream-border bg-white px-3 py-2 text-sm"
              placeholder="Biofloc heat — ops WhatsApp group"
            />
          </label>
        </>
      ) : null}
    </CreamCard>
  );
}
