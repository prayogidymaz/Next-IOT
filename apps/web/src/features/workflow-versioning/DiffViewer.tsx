"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  fetchVersionDiff,
  fetchWorkflowVersions,
  type VersionDiff,
  type WorkflowVersionRecord,
} from "@/lib/api/workflowVersioning";

type Props = {
  workflowId: string;
  open: boolean;
  onClose: () => void;
  initialVersionAId?: string;
  initialVersionBId?: string;
};

function DiffSection({ title, items, tone }: { title: string; items: string[]; tone: "green" | "red" | "yellow" }) {
  const toneClass =
    tone === "green" ? "border-emerald-200 bg-emerald-50" : tone === "red" ? "border-red-200 bg-red-50" : "border-amber-200 bg-amber-50";
  return (
    <div className={`rounded-lg border p-3 ${toneClass}`}>
      <h4 className="text-sm font-semibold text-stone-800">{title}</h4>
      {items.length === 0 ? (
        <p className="mt-1 text-xs text-stone-500">None</p>
      ) : (
        <ul className="mt-2 max-h-32 list-inside list-disc overflow-y-auto text-xs text-stone-700">
          {items.map((id) => (
            <li key={id}>{id}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function DiffViewer({ workflowId, open, onClose, initialVersionAId, initialVersionBId }: Props) {
  const [versions, setVersions] = useState<WorkflowVersionRecord[]>([]);
  const [versionAId, setVersionAId] = useState(initialVersionAId ?? "");
  const [versionBId, setVersionBId] = useState(initialVersionBId ?? "");
  const [diff, setDiff] = useState<VersionDiff | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showJson, setShowJson] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    void fetchWorkflowVersions(workflowId)
      .then(setVersions)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load versions"));
  }, [open, workflowId]);

  useEffect(() => {
    if (initialVersionAId) setVersionAId(initialVersionAId);
    if (initialVersionBId) setVersionBId(initialVersionBId);
  }, [initialVersionAId, initialVersionBId]);

  const snapshotPair = useMemo(() => {
    const a = versions.find((v) => v.id === versionAId);
    const b = versions.find((v) => v.id === versionBId);
    return { a, b };
  }, [versionAId, versionBId, versions]);

  const loadDiff = useCallback(async () => {
    if (!versionAId || !versionBId || versionAId === versionBId) {
      setError("Select two different versions");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await fetchVersionDiff(workflowId, versionAId, versionBId);
      setDiff(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Diff failed");
      setDiff(null);
    } finally {
      setLoading(false);
    }
  }, [versionAId, versionBId, workflowId]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="flex max-h-[90vh] w-full max-w-3xl flex-col rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-stone-200 px-4 py-3">
          <h2 className="text-lg font-semibold text-stone-900">Version diff</h2>
          <button type="button" className="text-sm text-stone-600 hover:text-stone-900" onClick={onClose}>
            Close
          </button>
        </div>
        <div className="space-y-4 overflow-y-auto p-4">
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block text-xs font-medium text-stone-600">
              Version A
              <select
                className="mt-1 w-full rounded border border-stone-300 px-2 py-1.5 text-sm"
                value={versionAId}
                onChange={(e) => setVersionAId(e.target.value)}
              >
                <option value="">Select…</option>
                {versions.map((v) => (
                  <option key={v.id} value={v.id}>
                    v{v.version_number} {v.is_active ? "(active)" : ""}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-xs font-medium text-stone-600">
              Version B
              <select
                className="mt-1 w-full rounded border border-stone-300 px-2 py-1.5 text-sm"
                value={versionBId}
                onChange={(e) => setVersionBId(e.target.value)}
              >
                <option value="">Select…</option>
                {versions.map((v) => (
                  <option key={v.id} value={v.id}>
                    v{v.version_number} {v.is_active ? "(active)" : ""}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <button
            type="button"
            disabled={loading}
            className="rounded-lg bg-stone-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            onClick={() => void loadDiff()}
          >
            {loading ? "Loading…" : "Compare"}
          </button>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          {diff ? (
            <>
              <div className="grid gap-3 sm:grid-cols-3">
                <DiffSection title="Added nodes" items={diff.added_nodes} tone="green" />
                <DiffSection title="Removed nodes" items={diff.removed_nodes} tone="red" />
                <DiffSection title="Modified nodes" items={diff.modified_nodes} tone="yellow" />
              </div>
              <label className="flex items-center gap-2 text-sm text-stone-700">
                <input type="checkbox" checked={showJson} onChange={(e) => setShowJson(e.target.checked)} />
                Side-by-side snapshot JSON
              </label>
              {showJson ? (
                <div className="grid gap-3 sm:grid-cols-2">
                  <pre className="max-h-48 overflow-auto rounded border bg-stone-50 p-2 text-[10px]">
                    {JSON.stringify(snapshotPair.a?.snapshot_json ?? {}, null, 2)}
                  </pre>
                  <pre className="max-h-48 overflow-auto rounded border bg-stone-50 p-2 text-[10px]">
                    {JSON.stringify(snapshotPair.b?.snapshot_json ?? {}, null, 2)}
                  </pre>
                </div>
              ) : null}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
