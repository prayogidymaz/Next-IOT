"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

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

  return (
    <div className="space-y-4 p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold text-stone-900">Workflow analytics</h1>
        <div className="flex gap-2">
          {PERIODS.map((d) => (
            <button
              key={d}
              type="button"
              className={`rounded-lg px-3 py-1.5 text-sm ${period === d ? "bg-stone-900 text-white" : "border border-stone-300"}`}
              onClick={() => setPeriod(d)}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-stone-200">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-stone-50 text-xs uppercase text-stone-500">
            <tr>
              <th className="px-4 py-3">Rank</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Fire count</th>
              <th className="px-4 py-3">Success rate</th>
              <th className="px-4 py-3">Avg duration</th>
              <th className="px-4 py-3">Savings (IDR)</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={row.workflow_id} className="border-t border-stone-100">
                <td className="px-4 py-3">{idx + 1}</td>
                <td className="px-4 py-3">
                  <Link href={`/analytics/workflows/${row.workflow_id}`} className="font-medium text-emerald-800 hover:underline">
                    {row.name}
                  </Link>
                </td>
                <td className="px-4 py-3">{row.fire_count}</td>
                <td className="px-4 py-3">{successRate(row)}</td>
                <td className="px-4 py-3">{Math.round(row.avg_duration_ms)} ms</td>
                <td className="px-4 py-3">{row.savings_idr_estimate.toLocaleString("id-ID")}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {loading ? <p className="p-4 text-sm text-stone-500">Loading…</p> : null}
        {!loading && rows.length === 0 ? <p className="p-4 text-sm text-stone-500">No data for this period.</p> : null}
      </div>
    </div>
  );
}
