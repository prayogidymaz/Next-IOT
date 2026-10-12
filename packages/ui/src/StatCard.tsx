import type { ReactNode } from "react";

import { Card } from "./Card";

type StatCardProps = {
  title: string;
  value: string;
  subtitle?: string;
  trend?: { direction: "up" | "down"; label: string };
  icon: ReactNode;
};

export function StatCard({ title, value, subtitle, trend, icon }: StatCardProps) {
  return (
    <Card className="p-5" shadow="sm">
      <div className="flex items-start justify-between gap-3">
        <span className="rounded-full bg-sky-50 p-2.5 text-sky-600">{icon}</span>
        {trend ? (
          <span
            className={`text-xs font-medium ${trend.direction === "up" ? "text-emerald-600" : "text-red-600"}`}
          >
            {trend.direction === "up" ? "↑" : "↓"} {trend.label}
          </span>
        ) : null}
      </div>
      <p className="mt-4 text-xs font-medium uppercase tracking-wide text-slate-500">{title}</p>
      <p className="mt-1 font-mono text-2xl font-semibold tabular-nums text-slate-900">{value}</p>
      {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
    </Card>
  );
}
