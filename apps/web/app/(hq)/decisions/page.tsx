"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
import { Button } from "@/components/ui/button";
import {
  acceptRecommendation,
  listDecisionRecommendations,
  rejectRecommendation,
  type DecisionRecommendation,
} from "@/lib/api/decisions";
import { TableSkeleton } from "@/src/components/LoadingSkeleton";
import { EmptyState } from "@/src/components/ui/EmptyState";

export default function DecisionsPage() {
  const [rows, setRows] = useState<DecisionRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setRows(await listDecisionRecommendations());
    } catch {
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <HqPageShell
      action={
        <div className="flex gap-2">
          <Link href="/decisions/policies" className="text-sm text-primary">
            Policies
          </Link>
          <Link href="/decisions/outcomes" className="text-sm text-primary">
            Outcomes
          </Link>
        </div>
      }
    >
      {loading ? (
        <TableSkeleton rows={4} />
      ) : rows.length === 0 ? (
        <EmptyState title="No pending recommendations" description="Run the daily decision tick or generate from API." />
      ) : (
        <ul className="space-y-3">
          {rows.map((r) => (
            <li key={r.id} className="rounded-xl border border-border bg-card p-4 text-sm">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-foreground">{r.recommendation_type}</p>
                  <p className="text-muted-foreground">Confidence {(r.confidence * 100).toFixed(0)}% · {r.status}</p>
                </div>
                <div className="flex gap-2">
                  <Button type="button" size="sm" onClick={() => void acceptRecommendation(r.id).then(load)}>
                    Accept
                  </Button>
                  <Button type="button" size="sm" variant="outline" onClick={() => void rejectRecommendation(r.id).then(load)}>
                    Reject
                  </Button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </HqPageShell>
  );
}
