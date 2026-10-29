"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import {
  fetchWorkflowFailures,
  fetchWorkflowSavings,
  fetchWorkflowTimeline,
  type FailureReport,
  type SavingsReport,
  type TimelinePoint,
} from "@/lib/api/workflowAnalytics";

type Props = { workflowId: string };

export function WorkflowAnalyticsDetail({ workflowId }: Props) {
  const [period] = useState(30);
  const [points, setPoints] = useState<TimelinePoint[]>([]);
  const [savings, setSavings] = useState<SavingsReport | null>(null);
  const [failures, setFailures] = useState<FailureReport | null>(null);

  useEffect(() => {
    void fetchWorkflowTimeline(workflowId, period).then((d) => setPoints(d.points));
    void fetchWorkflowSavings(workflowId).then(setSavings);
    void fetchWorkflowFailures(workflowId).then(setFailures);
  }, [workflowId, period]);

  return (
    <div className="space-y-6 p-6">
      <Link href="/analytics/workflows" className="text-sm text-stone-600 hover:text-stone-900">
        ← Workflow analytics
      </Link>
      <h1 className="text-2xl font-semibold text-stone-900">Workflow {workflowId.slice(0, 8)}…</h1>

      <section className="rounded-xl border border-stone-200 bg-white p-4">
        <h2 className="text-sm font-semibold text-stone-800">Fires per day ({period}d)</h2>
        <div className="mt-4 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="fire_count" stroke="#166534" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {savings ? (
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-stone-200 bg-emerald-50 p-4">
            <p className="text-xs text-stone-600">Water saved</p>
            <p className="text-xl font-semibold text-stone-900">{savings.water_liters_saved.toLocaleString()} L</p>
          </div>
          <div className="rounded-xl border border-stone-200 bg-sky-50 p-4">
            <p className="text-xs text-stone-600">Energy saved</p>
            <p className="text-xl font-semibold text-stone-900">{savings.kwh_saved.toLocaleString()} kWh</p>
          </div>
          <div className="rounded-xl border border-stone-200 bg-amber-50 p-4">
            <p className="text-xs text-stone-600">Total savings</p>
            <p className="text-xl font-semibold text-stone-900">Rp {savings.idr_total.toLocaleString("id-ID")}</p>
          </div>
        </div>
      ) : null}

      {failures ? (
        <section className="rounded-xl border border-stone-200 p-4">
          <h2 className="text-sm font-semibold text-stone-800">Failure analysis</h2>
          <p className="mt-1 text-sm text-stone-600">Failure rate: {(failures.failure_rate * 100).toFixed(1)}%</p>
          {failures.failed_at_step ? <p className="text-sm text-stone-600">Often fails at: {failures.failed_at_step}</p> : null}
          <ul className="mt-2 list-inside list-disc text-sm text-stone-700">
            {failures.common_errors.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
          <p className="mt-3 rounded-lg bg-stone-50 p-3 text-sm text-stone-800">
            <span className="font-medium">Suggested fix:</span> {failures.suggested_fix}
          </p>
        </section>
      ) : null}
    </div>
  );
}
