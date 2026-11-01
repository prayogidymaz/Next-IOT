"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
import { listReportTemplates, type ReportTemplate } from "@/lib/api/reports";
import { TableSkeleton } from "@/src/components/LoadingSkeleton";
import { EmptyState } from "@/src/components/ui/EmptyState";

export default function ReportsPage() {
  const [rows, setRows] = useState<ReportTemplate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void listReportTemplates()
      .then(setRows)
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <HqPageShell
      action={
        <Link href="/reports/builder" className="rounded-lg bg-foreground px-4 py-2 text-sm text-background">
          New report
        </Link>
      }
    >
      {loading ? (
        <TableSkeleton rows={5} />
      ) : rows.length === 0 ? (
        <EmptyState title="No report templates" description="Build a drag-drop report template." action={<Link href="/reports/builder" className="text-sm text-primary">Open builder</Link>} />
      ) : (
        <ul className="divide-y divide-border rounded-xl border border-border bg-card">
          {rows.map((r) => (
            <li key={r.id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm">
              <div>
                <p className="font-medium text-foreground">{r.name}</p>
                <p className="text-muted-foreground">{r.description}</p>
              </div>
              <div className="flex gap-2">
                <Link href={`/reports/${r.id}/schedule`} className="text-primary">
                  Schedule
                </Link>
                <Link href={`/reports/${r.id}/history`} className="text-primary">
                  History
                </Link>
              </div>
            </li>
          ))}
        </ul>
      )}
    </HqPageShell>
  );
}
