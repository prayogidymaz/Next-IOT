"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { StatCard } from "@/src/components/ui/StatCard";
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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    void Promise.all([
      fetchWorkflowTimeline(workflowId, period).then((d) => setPoints(d.points)),
      fetchWorkflowSavings(workflowId).then(setSavings),
      fetchWorkflowFailures(workflowId).then(setFailures),
    ]).finally(() => setLoading(false));
  }, [workflowId, period]);

  const fireCount = points.reduce((sum, p) => sum + p.fire_count, 0);
  const successRate = failures ? `${((1 - failures.failure_rate) * 100).toFixed(0)}%` : "—";

  return (
    <div className="container mx-auto space-y-6 px-4 py-6 md:px-6 lg:px-8">
      <Link href="/analytics/workflows" className="text-sm text-muted-foreground hover:text-foreground">
        ← Workflow analytics
      </Link>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard title="Total fires" value={fireCount} loading={loading} />
        <StatCard title="Success rate" value={successRate} loading={loading} />
        <StatCard
          title="Savings (IDR)"
          value={savings ? savings.idr_total.toLocaleString("id-ID") : "—"}
          loading={loading}
          empty={!loading && !savings}
        />
      </div>

      <section className="rounded-xl border border-border bg-card p-4">
        <h2 className="text-sm font-semibold text-foreground">Fires per day ({period}d)</h2>
        <div className="mt-4 h-64 w-full md:h-72">
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
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <StatCard title="Water saved" value={savings.water_liters_saved.toLocaleString()} unit="L" />
          <StatCard title="Energy saved" value={savings.kwh_saved.toLocaleString()} unit="kWh" />
          <StatCard title="Total savings" value={savings.idr_total.toLocaleString("id-ID")} unit="IDR" />
        </div>
      ) : null}

      {failures ? (
        <section className="rounded-xl border border-border bg-card p-4">
          <h2 className="text-sm font-semibold text-foreground">Failure analysis</h2>
          <p className="mt-1 text-sm text-muted-foreground">Failure rate: {(failures.failure_rate * 100).toFixed(1)}%</p>
          {failures.failed_at_step ? <p className="text-sm text-muted-foreground">Often fails at: {failures.failed_at_step}</p> : null}
          <ul className="mt-2 list-inside list-disc text-sm text-foreground">
            {failures.common_errors.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
          <p className="mt-3 rounded-lg bg-muted p-3 text-sm text-foreground">
            <span className="font-medium">Suggested fix:</span> {failures.suggested_fix}
          </p>
        </section>
      ) : null}
    </div>
  );
}
