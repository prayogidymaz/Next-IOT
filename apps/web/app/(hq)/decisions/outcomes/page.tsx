"use client";

import { useEffect, useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
import { fetchOutcomeSummary } from "@/lib/api/decisions";

export default function DecisionOutcomesPage() {
  const [summary, setSummary] = useState<Record<string, number>>({});

  useEffect(() => {
    void fetchOutcomeSummary().then(setSummary).catch(() => setSummary({}));
  }, []);

  return (
    <HqPageShell>
      <div className="rounded-xl border border-border bg-card p-4 text-sm">
        <p className="font-medium text-foreground">Historical success rate</p>
        <dl className="mt-3 space-y-2">
          {Object.entries(summary).map(([key, value]) => (
            <div key={key} className="flex justify-between gap-4">
              <dt className="text-muted-foreground">{key}</dt>
              <dd className="font-mono text-foreground">{(value * 100).toFixed(1)}%</dd>
            </div>
          ))}
          {Object.keys(summary).length === 0 ? <p className="text-muted-foreground">No outcome data yet.</p> : null}
        </dl>
      </div>
    </HqPageShell>
  );
}
