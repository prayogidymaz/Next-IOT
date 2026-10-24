"use client";

import type { Node } from "@xyflow/react";

import type { MeshWorkflowNodeData } from "@/lib/studio/mesh-workflow-flow";

type Props = {
  node: Node<MeshWorkflowNodeData> | null;
  onChange: (nodeId: string, patch: Partial<MeshWorkflowNodeData>) => void;
};

export function MeshWorkflowPropertyPanel({ node, onChange }: Props) {
  if (!node) {
    return (
      <div className="rounded-2xl border border-cream-border bg-white p-4 text-sm text-ink-secondary">
        Select a mesh workflow node
      </div>
    );
  }

  const d = node.data;

  return (
    <div className="space-y-3 rounded-2xl border border-cream-border bg-white p-4">
      <h3 className="text-sm font-semibold text-ink-primary">Node properties</h3>
      <label className="block text-xs text-ink-secondary">
        Label
        <input
          className="mt-1 w-full rounded-xl border border-cream-border px-2 py-1 text-sm"
          value={d.label}
          onChange={(e) => onChange(node.id, { label: e.target.value })}
        />
      </label>
      {d.kind === "mesh_event" ? (
        <>
          <label className="block text-xs text-ink-secondary">
            Domain
            <input
              className="mt-1 w-full rounded-xl border border-cream-border px-2 py-1 text-sm"
              value={d.domain ?? ""}
              onChange={(e) => onChange(node.id, { domain: e.target.value })}
            />
          </label>
          <label className="block text-xs text-ink-secondary">
            Event type
            <input
              className="mt-1 w-full rounded-xl border border-cream-border px-2 py-1 text-sm"
              value={d.eventType ?? ""}
              onChange={(e) => onChange(node.id, { eventType: e.target.value })}
            />
          </label>
        </>
      ) : null}
      {d.kind === "device_resolver" ? (
        <>
          <label className="block text-xs text-ink-secondary">
            Capability
            <input
              className="mt-1 w-full rounded-xl border border-cream-border px-2 py-1 text-sm"
              value={d.capability ?? ""}
              onChange={(e) => onChange(node.id, { capability: e.target.value })}
            />
          </label>
          <label className="block text-xs text-ink-secondary">
            Zone
            <input
              className="mt-1 w-full rounded-xl border border-cream-border px-2 py-1 text-sm"
              value={d.zone ?? ""}
              onChange={(e) => onChange(node.id, { zone: e.target.value })}
            />
          </label>
        </>
      ) : null}
      {d.kind === "dispatch_device" ? (
        <>
          <label className="block text-xs text-ink-secondary">
            Command
            <input
              className="mt-1 w-full rounded-xl border border-cream-border px-2 py-1 text-sm"
              value={d.command ?? ""}
              onChange={(e) => onChange(node.id, { command: e.target.value })}
            />
          </label>
          <label className="block text-xs text-ink-secondary">
            Params JSON
            <textarea
              className="mt-1 w-full rounded-xl border border-cream-border px-2 py-1 font-mono text-xs"
              rows={4}
              value={d.configJson ?? "{}"}
              onChange={(e) => onChange(node.id, { configJson: e.target.value })}
            />
          </label>
        </>
      ) : null}
      {d.kind === "wait_for_event" ? (
        <>
          <label className="block text-xs text-ink-secondary">
            Wait domain
            <input
              className="mt-1 w-full rounded-xl border border-cream-border px-2 py-1 text-sm"
              value={d.waitDomain ?? ""}
              onChange={(e) => onChange(node.id, { waitDomain: e.target.value })}
            />
          </label>
          <label className="block text-xs text-ink-secondary">
            Wait event type
            <input
              className="mt-1 w-full rounded-xl border border-cream-border px-2 py-1 text-sm"
              value={d.waitEventType ?? ""}
              onChange={(e) => onChange(node.id, { waitEventType: e.target.value })}
            />
          </label>
        </>
      ) : null}
    </div>
  );
}
