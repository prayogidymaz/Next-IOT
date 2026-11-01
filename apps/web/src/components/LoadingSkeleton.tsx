"use client";

import { cn } from "@/src/lib/cn";

function Block({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-md bg-muted", className)} />;
}

export function CardSkeleton() {
  return (
    <div className="space-y-3 rounded-lg border border-border bg-card p-4">
      <Block className="h-3 w-24" />
      <Block className="h-8 w-40" />
    </div>
  );
}

export function TableSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="space-y-2 rounded-xl border border-border bg-card p-2">
      {Array.from({ length: rows }).map((_, i) => (
        <Block key={i} className="h-10 w-full" />
      ))}
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <Block className="mb-4 h-4 w-32" />
      <Block className="h-48 w-full" />
    </div>
  );
}

export function ListSkeleton({ lines = 5 }: { lines?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <Block key={i} className="h-4 w-full" />
      ))}
    </div>
  );
}

export function GridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}
