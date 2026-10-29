"use client";

import { useState } from "react";

import { getApiBaseUrl } from "@/lib/auth/api";
import { useHqToast } from "@/hooks/useHqToast";

import { useCanActivateWorkflow } from "./useCanActivateWorkflow";

type Props = {
  workflowId: string;
  token: string;
  enabled: boolean;
  onToggled?: (enabled: boolean) => void;
};

export function WorkflowActivateButton({ workflowId, token, enabled, onToggled }: Props) {
  const { showToast } = useHqToast();
  const { loading, canActivate, blockedReason, refresh } = useCanActivateWorkflow(workflowId);
  const [busy, setBusy] = useState(false);

  const blocked = !enabled && !canActivate;

  async function toggleActivate() {
    if (blocked) return;
    setBusy(true);
    try {
      const getRes = await fetch(`${getApiBaseUrl()}/api/v1/mesh/workflows/${workflowId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!getRes.ok) throw new Error("Failed to load workflow");
      const record = (await getRes.json()) as { definition: Record<string, unknown> };
      const payload = { ...record.definition, enabled: !enabled };
      const res = await fetch(`${getApiBaseUrl()}/api/v1/mesh/workflows/${workflowId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const text = await res.text();
        showToast(text || `Activation failed (${res.status})`, "error");
        refresh();
        return;
      }
      showToast(enabled ? "Workflow deactivated" : "Workflow activated", "success");
      onToggled?.(!enabled);
      refresh();
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Activation failed", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <span className="inline-flex" title={blocked && blockedReason ? blockedReason : undefined}>
      <button
        type="button"
        disabled={loading || busy || blocked}
        className="rounded border border-emerald-600 px-2 py-1 text-sm text-emerald-800 disabled:cursor-not-allowed disabled:opacity-50"
        onClick={() => void toggleActivate()}
      >
        {busy ? "…" : enabled ? "Deactivate" : "Activate"}
      </button>
    </span>
  );
}
