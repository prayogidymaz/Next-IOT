"use client";

import { useEffect, useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
import { Button } from "@/components/ui/button";
import { createAutoActionPolicy, listAutoActionPolicies, type AutoActionPolicy } from "@/lib/api/decisions";

export default function DecisionPoliciesPage() {
  const [rows, setRows] = useState<AutoActionPolicy[]>([]);
  const [triggerType, setTriggerType] = useState("threshold_optimization");
  const [minConfidence, setMinConfidence] = useState(0.85);

  useEffect(() => {
    void listAutoActionPolicies().then(setRows).catch(() => setRows([]));
  }, []);

  async function addPolicy() {
    const row = await createAutoActionPolicy({
      trigger_type: triggerType,
      min_confidence: minConfidence,
      auto_apply: false,
      approval_required: true,
    });
    setRows((prev) => [...prev, row]);
  }

  return (
    <HqPageShell>
      <form
        className="mb-6 flex max-w-xl flex-wrap gap-3 rounded-xl border border-border bg-card p-4 text-sm"
        onSubmit={(e) => {
          e.preventDefault();
          void addPolicy();
        }}
      >
        <label className="flex flex-col gap-1">
          Trigger
          <input className="rounded border border-border bg-background px-2 py-1" value={triggerType} onChange={(e) => setTriggerType(e.target.value)} />
        </label>
        <label className="flex flex-col gap-1">
          Min confidence
          <input
            type="number"
            min={0}
            max={1}
            step={0.01}
            className="rounded border border-border bg-background px-2 py-1"
            value={minConfidence}
            onChange={(e) => setMinConfidence(Number(e.target.value))}
          />
        </label>
        <Button type="submit" className="self-end">
          Add policy
        </Button>
      </form>
      <ul className="divide-y divide-border rounded-xl border border-border bg-card text-sm">
        {rows.map((p) => (
          <li key={p.id} className="px-4 py-3">
            {p.trigger_type} — min {(p.min_confidence * 100).toFixed(0)}% · auto {p.auto_apply ? "yes" : "no"}
          </li>
        ))}
      </ul>
    </HqPageShell>
  );
}
