"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/src/components/ui/DataTable";
import { EmptyState } from "@/src/components/ui/EmptyState";
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
  const [loading, setLoading] = useState(true);
  const [workflowFilter, setWorkflowFilter] = useState("");
  const [requesterFilter, setRequesterFilter] = useState("");
  const [decision, setDecision] = useState<Decision | null>(null);
  const [notes, setNotes] = useState("");

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      setRows(await fetchPendingApprovals());
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Load failed", "error");
    } finally {
      setLoading(false);
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

  const columns = useMemo<Array<DataTableColumn<ApprovalRequestRecord>>>(
    () => [
      {
        id: "workflow",
        header: "Workflow",
        render: (r) => <span className="font-mono text-xs">{r.workflow_id.slice(0, 8)}…</span>,
      },
      {
        id: "requester",
        header: "Requester",
        render: (r) => <span className="font-mono text-xs">{r.requested_by.slice(0, 8)}…</span>,
      },
      { id: "requested", header: "Requested", render: (r) => new Date(r.requested_at).toLocaleString() },
      { id: "notes", header: "Notes", render: (r) => r.notes || "—" },
      {
        id: "actions",
        header: "Actions",
        render: (r) => (
          <div className="flex gap-2">
            <button type="button" className="rounded bg-emerald-600 px-2 py-1 text-xs text-white" onClick={() => setDecision({ id: r.id, action: "approve" })}>
              Approve
            </button>
            <button type="button" className="rounded border border-border px-2 py-1 text-xs" onClick={() => setDecision({ id: r.id, action: "reject" })}>
              Reject
            </button>
          </div>
        ),
      },
    ],
    [],
  );

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
    <div className="container mx-auto space-y-4 px-4 py-6 md:px-6 lg:px-8">
      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground"
          placeholder="Filter workflow id"
          value={workflowFilter}
          onChange={(e) => setWorkflowFilter(e.target.value)}
        />
        <input
          className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground"
          placeholder="Filter requester id"
          value={requesterFilter}
          onChange={(e) => setRequesterFilter(e.target.value)}
        />
      </div>

      {!loading && filtered.length === 0 ? (
        <EmptyState title="No pending approvals" description="New requests will appear here." />
      ) : (
        <DataTable columns={columns} rows={filtered} rowKey={(r) => r.id} loading={loading} emptyTitle="No pending approvals" />
      )}

      {decision ? (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center">
          <div className="w-full max-w-md rounded-xl border border-border bg-card p-4 shadow-lg">
            <h2 className="text-lg font-semibold capitalize text-foreground">{decision.action} request</h2>
            <textarea className="mt-3 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Notes (optional)" />
            <div className="mt-3 flex justify-end gap-2">
              <button type="button" className="rounded-lg border border-border px-3 py-2 text-sm" onClick={() => setDecision(null)}>
                Cancel
              </button>
              <button type="button" className="rounded-lg bg-foreground px-3 py-2 text-sm text-background" onClick={() => void submitDecision()}>
                Confirm
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
