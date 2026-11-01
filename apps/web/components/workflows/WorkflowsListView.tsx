"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { listMeshWorkflows, type MeshWorkflowListItem } from "@/lib/api/meshWorkflows";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { ErrorState } from "@/src/components/ui/ErrorState";
import { TableSkeleton } from "@/src/components/LoadingSkeleton";

export function WorkflowsListView() {
  const [rows, setRows] = useState<MeshWorkflowListItem[]>([]);
  const [status, setStatus] = useState<"all" | "enabled" | "disabled">("all");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await listMeshWorkflows({
        enabled: status === "all" ? undefined : status === "enabled",
        search: search.trim() || undefined,
      });
      setRows(list);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Load failed");
    } finally {
      setLoading(false);
    }
  }, [search, status]);

  useEffect(() => {
    const t = window.setTimeout(() => void load(), search ? 300 : 0);
    return () => window.clearTimeout(t);
  }, [load, search]);

  const filtered = useMemo(() => {
    if (status === "all") return rows;
    return rows.filter((r) => (status === "enabled" ? r.enabled : !r.enabled));
  }, [rows, status]);

  if (loading) return <TableSkeleton rows={6} />;
  if (error) return <ErrorState error={error} onRetry={() => void load()} />;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap gap-2">
          <select
            className="rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground"
            value={status}
            onChange={(e) => setStatus(e.target.value as "all" | "enabled" | "disabled")}
          >
            <option value="all">All status</option>
            <option value="enabled">Enabled</option>
            <option value="disabled">Disabled</option>
          </select>
          <input
            className="min-w-[12rem] rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground"
            placeholder="Search workflows…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Link href="/workflows/new" className="rounded-lg bg-foreground px-4 py-2 text-sm text-background">
          + New workflow
        </Link>
      </div>
      {filtered.length === 0 ? (
        <EmptyState
          title="No workflows"
          description="Create your first automation workflow."
          action={
            <Link href="/workflows/new" className="rounded-lg bg-foreground px-4 py-2 text-sm text-background">
              + New workflow
            </Link>
          }
        />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-border bg-card">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-border bg-muted/40 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Last fired</th>
                <th className="px-4 py-3">Success rate</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((w) => (
                <tr key={w.id} className="cursor-pointer hover:bg-muted/30" onClick={() => (window.location.href = `/workflows/${w.id}`)}>
                  <td className="px-4 py-3 font-medium text-foreground">{w.name}</td>
                  <td className="px-4 py-3 text-muted-foreground">{w.enabled ? "Enabled" : "Disabled"}</td>
                  <td className="px-4 py-3 text-muted-foreground">{w.last_fired_at ? new Date(w.last_fired_at).toLocaleString() : "—"}</td>
                  <td className="px-4 py-3 text-muted-foreground">{w.success_rate_percent ?? 0}%</td>
                  <td className="px-4 py-3 text-muted-foreground">{w.action_count ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
