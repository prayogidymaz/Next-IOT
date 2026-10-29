"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  approveRequest,
  fetchPendingApprovals,
  rejectRequest,
  type ApprovalRequestRecord,
} from "@/lib/api/workflowApproval";
import { useHqToast } from "@/hooks/useHqToast";

type Decision = { id: string; action: "approve" | "reject" };

export function PendingApprovalsPage() {
  const { showToast } = useHqToast();
  const [rows, setRows] = useState<ApprovalRequestRecord[]>([]);
  const [workflowFilter, setWorkflowFilter] = useState("");
  const [requesterFilter, setRequesterFilter] = useState("");
  const [decision, setDecision] = useState<Decision | null>(null);
  const [notes, setNotes] = useState("");

  const reload = useCallback(async () => {
    try {
      setRows(await fetchPendingApprovals());
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Load failed", "error");
    }
  }, [showToast]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const filtered = useMemo(() => {
    return rows.filter((r) => {
      const wf = r.workflow_id.toLowerCase().includes(workflowFilter.trim().toLowerCase());
      const req = r.requested_by.toLowerCase().includes(requesterFilter.trim().toLowerCase());
      return wf && req;
    });
  }, [rows, workflowFilter, requesterFilter]);

  async function submitDecision() {
    if (!decision) return;
    try {
      if (decision.action === "approve") await approveRequest(decision.id, notes);
      else await rejectRequest(decision.id, notes);
      showToast(decision.action === "approve" ? "Approved" : "Rejected", "success");
      setDecision(null);
      setNotes("");
      await reload();
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Action failed", "error");
    }
  }

  return (
    <div className="space-y-4 p-6">
      <h1 className="text-2xl font-semibold text-stone-900">Pending approvals</h1>
      <div className="flex flex-wrap gap-3">
        <input
          className="rounded-lg border border-stone-300 px-3 py-2 text-sm"
          placeholder="Filter workflow id"
          value={workflowFilter}
          onChange={(e) => setWorkflowFilter(e.target.value)}
        />
        <input
          className="rounded-lg border border-stone-300 px-3 py-2 text-sm"
          placeholder="Filter requester id"
          value={requesterFilter}
          onChange={(e) => setRequesterFilter(e.target.value)}
        />
      </div>
      <div className="overflow-x-auto rounded-xl border border-stone-200">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-stone-50 text-xs uppercase text-stone-500">
            <tr>
              <th className="px-4 py-3">Workflow</th>
              <th className="px-4 py-3">Requester</th>
              <th className="px-4 py-3">Requested</th>
              <th className="px-4 py-3">Notes</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.id} className="border-t border-stone-100">
                <td className="px-4 py-3 font-mono text-xs">{r.workflow_id.slice(0, 8)}…</td>
                <td className="px-4 py-3 font-mono text-xs">{r.requested_by.slice(0, 8)}…</td>
                <td className="px-4 py-3">{new Date(r.requested_at).toLocaleString()}</td>
                <td className="max-w-xs truncate px-4 py-3">{r.notes || "—"}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button
                      type="button"
                      className="rounded bg-emerald-600 px-2 py-1 text-xs text-white"
                      onClick={() => setDecision({ id: r.id, action: "approve" })}
                    >
                      Approve
                    </button>
                    <button
                      type="button"
                      className="rounded bg-red-600 px-2 py-1 text-xs text-white"
                      onClick={() => setDecision({ id: r.id, action: "reject" })}
                    >
                      Reject
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 ? <p className="p-4 text-sm text-stone-500">No pending requests.</p> : null}
      </div>

      {decision ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-4">
            <h2 className="text-lg font-semibold capitalize">{decision.action} request</h2>
            <textarea
              className="mt-3 w-full rounded border px-3 py-2 text-sm"
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Decision notes (optional)"
            />
            <div className="mt-4 flex justify-end gap-2">
              <button type="button" className="rounded border px-3 py-1.5 text-sm" onClick={() => setDecision(null)}>
                Cancel
              </button>
              <button type="button" className="rounded bg-stone-900 px-3 py-1.5 text-sm text-white" onClick={() => void submitDecision()}>
                Confirm
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
