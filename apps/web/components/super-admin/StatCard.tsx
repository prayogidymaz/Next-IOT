"use client";

import type { LucideIcon } from "lucide-react";

import { CreamCard } from "@/components/ui/CreamCard";

type StatCardProps = {
  title: string;
  value: string;
  subtitle: string;
  icon: LucideIcon;
  iconClass: string;
  iconBgClass: string;
};

export function StatCard({ title, value, subtitle, icon: Icon, iconClass, iconBgClass }: StatCardProps) {
  return (
    <CreamCard className="p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium uppercase tracking-wide text-ink-tertiary">{title}</p>
          <p className="mt-2 text-2xl font-semibold tabular-nums text-ink-primary">{value}</p>
          <p className="mt-1 text-sm text-ink-secondary">{subtitle}</p>
        </div>
        <span className={`rounded-xl p-2.5 ${iconBgClass}`}>
          <Icon className={`h-5 w-5 ${iconClass}`} />
        </span>
      </div>
    </CreamCard>
  );
}
