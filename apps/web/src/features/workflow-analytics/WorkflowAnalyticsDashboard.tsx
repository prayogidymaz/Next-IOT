"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/src/components/ui/DataTable";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { fetchTopFiredWorkflows, type WorkflowStatsRecord } from "@/lib/api/workflowAnalytics";

const PERIODS = [7, 30, 90] as const;

function successRate(row: WorkflowStatsRecord): string {
  if (row.fire_count === 0) return "—";
  return `${Math.round((row.success_count / row.fire_count) * 100)}%`;
}

export function WorkflowAnalyticsDashboard() {
  const [period, setPeriod] = useState<number>(30);
  const [rows, setRows] = useState<WorkflowStatsRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    void fetchTopFiredWorkflows(period)
      .then(setRows)
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  }, [period]);

  const columns = useMemo<Array<DataTableColumn<WorkflowStatsRecord>>>(
    () => [
      {
        id: "rank",
        header: "Rank",
        render: (row) => rows.indexOf(row) + 1,
      },
      {
        id: "name",
        header: "Name",
        render: (row) => (
          <Link href={`/analytics/workflows/${row.workflow_id}`} className="font-medium text-emerald-700 hover:underline dark:text-emerald-400">
            {row.name}
          </Link>
        ),
      },
      { id: "fires", header: "Fire count", sortable: true, render: (row) => row.fire_count },
      { id: "success", header: "Success rate", render: (row) => successRate(row) },
      { id: "duration", header: "Avg duration", render: (row) => `${Math.round(row.avg_duration_ms)} ms` },
      {
        id: "savings",
        header: "Savings (IDR)",
        render: (row) => row.savings_idr_estimate.toLocaleString("id-ID"),
      },
    ],
    [rows],
  );

  return (
    <div className="container mx-auto space-y-4 px-4 py-6 md:px-6 lg:px-8">
      <div className="flex justify-end">
        <div className="flex flex-wrap gap-2">
          {PERIODS.map((d) => (
            <button
              key={d}
              type="button"
              className={`rounded-lg px-3 py-1.5 text-sm ${period === d ? "bg-foreground text-background" : "border border-border bg-card text-foreground"}`}
              onClick={() => setPeriod(d)}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {!loading && rows.length === 0 ? (
        <EmptyState title="No analytics data" description="Try a longer period or run workflows first." />
      ) : (
        <DataTable columns={columns} rows={rows} rowKey={(r) => r.workflow_id} loading={loading} pageSize={10} />
      )}
    </div>
  );
}
