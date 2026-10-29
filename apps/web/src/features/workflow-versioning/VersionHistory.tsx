"use client";

import { useCallback, useEffect, useState } from "react";

import {
  fetchWorkflowVersions,
  rollbackWorkflowVersion,
  type WorkflowVersionRecord,
} from "@/lib/api/workflowVersioning";
import { useHqToast } from "@/hooks/useHqToast";

import { DiffViewer } from "./DiffViewer";

type Props = {
  workflowId: string;
  onRollbackComplete?: () => void;
};

function formatCreator(createdBy: string | null): string {
  if (!createdBy) return "System";
  return createdBy.slice(0, 8);
}

export function VersionHistory({ workflowId, onRollbackComplete }: Props) {
  const { showToast } = useHqToast();
  const [rows, setRows] = useState<WorkflowVersionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmVersion, setConfirmVersion] = useState<number | null>(null);
  const [diffOpen, setDiffOpen] = useState(false);
  const [diffBaseId, setDiffBaseId] = useState<string | undefined>();
  const [diffCompare, setDiffCompare] = useState<string | undefined>();

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const list = await fetchWorkflowVersions(workflowId);
      setRows([...list].sort((a, b) => b.version_number - a.version_number));
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Failed to load versions", "error");
    } finally {
      setLoading(false);
    }
  }, [showToast, workflowId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  async function confirmRollback(versionNumber: number) {
    try {
      await rollbackWorkflowVersion(workflowId, versionNumber);
      showToast(`Rolled back to v${versionNumber}`, "success");
      setConfirmVersion(null);
      await reload();
      onRollbackComplete?.();
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Rollback failed", "error");
    }
  }

  function openDiffForRow(row: WorkflowVersionRecord) {
    const active = rows.find((r) => r.is_active);
    setDiffBaseId(row.id);
    setDiffOpen(true);
    if (active && active.id !== row.id) {
      setDiffCompare(active.id);
    }
  }

  return (
    <aside className="w-full max-w-md shrink-0 rounded-xl border border-stone-200 bg-white lg:w-80">
      <div className="border-b border-stone-200 px-4 py-3">
        <h2 className="text-sm font-semibold text-stone-900">Version history</h2>
        <p className="text-xs text-stone-500">Newest first</p>
      </div>
      <div className="max-h-[min(520px,60vh)] overflow-y-auto p-2">
        {loading ? <p className="p-3 text-sm text-stone-500">Loading…</p> : null}
        {!loading && rows.length === 0 ? <p className="p-3 text-sm text-stone-500">No versions yet.</p> : null}
        <ul className="space-y-2">
          {rows.map((row) => (
            <li key={row.id} className="rounded-lg border border-stone-100 bg-stone-50 p-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-sm font-medium text-stone-900">v{row.version_number}</p>
                  <p className="text-xs text-stone-500">{formatCreator(row.created_by)}</p>
                  <p className="text-xs text-stone-400">{new Date(row.created_at).toLocaleString()}</p>
                </div>
                {row.is_active ? (
                  <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-800">
                    Active
                  </span>
                ) : null}
              </div>
              <div className="mt-2 flex flex-wrap gap-2">
                {!row.is_active ? (
                  <button
                    type="button"
                    className="rounded border border-stone-300 px-2 py-1 text-xs hover:bg-white"
                    onClick={() => setConfirmVersion(row.version_number)}
                  >
                    Rollback
                  </button>
                ) : null}
                <button
                  type="button"
                  className="rounded border border-stone-300 px-2 py-1 text-xs hover:bg-white"
                  onClick={() => openDiffForRow(row)}
                >
                  Diff
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {confirmVersion !== null ? (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-sm rounded-xl bg-white p-4 shadow-lg">
            <p className="text-sm text-stone-800">
              Roll back workflow to <strong>v{confirmVersion}</strong>? Current canvas will be replaced.
            </p>
            <div className="mt-4 flex justify-end gap-2">
              <button type="button" className="rounded border px-3 py-1.5 text-sm" onClick={() => setConfirmVersion(null)}>
                Cancel
              </button>
              <button
                type="button"
                className="rounded bg-red-600 px-3 py-1.5 text-sm text-white"
                onClick={() => void confirmRollback(confirmVersion)}
              >
                Rollback
              </button>
            </div>
          </div>
        </div>
      ) : null}

      <DiffViewer
        workflowId={workflowId}
        open={diffOpen}
        onClose={() => setDiffOpen(false)}
        initialVersionAId={diffBaseId}
        initialVersionBId={diffCompare}
      />
    </aside>
  );
}
