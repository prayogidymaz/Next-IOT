"use client";

import type { ReactNode } from "react";

import { cn } from "@/src/lib/cn";

type Props = {
  title: string;
  value: string | number;
  unit?: string;
  trend?: string;
  icon?: ReactNode;
  color?: string;
  loading?: boolean;
  empty?: boolean;
};

export function StatCard({ title, value, unit, trend, icon, color, loading, empty }: Props) {
  if (loading) {
    return (
      <div className="flex flex-col gap-2 rounded-lg border border-border bg-card p-4">
        <div className="h-3 w-24 animate-pulse rounded bg-muted" />
        <div className="h-8 w-32 animate-pulse rounded bg-muted" />
      </div>
    );
  }

  if (empty) {
    return (
      <div className="flex flex-col gap-2 rounded-lg border border-dashed border-border bg-card p-4 text-muted-foreground">
        <span className="text-xs">{title}</span>
        <span className="text-sm">No data</span>
      </div>
    );
  }

  return (
    <div className={cn("flex flex-col gap-2 rounded-lg border border-border bg-card p-4", color)}>
      <div className="flex items-center justify-between gap-2 text-sm text-muted-foreground">
        <span>{title}</span>
        {icon ? <span aria-hidden>{icon}</span> : null}
      </div>
      <div className="text-2xl font-semibold text-foreground">
        {value}
        {unit ? <span className="ml-1 text-sm font-normal text-muted-foreground">{unit}</span> : null}
      </div>
      {trend ? <p className="text-xs text-muted-foreground">{trend}</p> : null}
    </div>
  );
}
