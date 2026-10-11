"use client";

import type { LucideIcon } from "lucide-react";

import { CommandCard } from "@/components/ui/CommandCard";

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
    <CommandCard className="p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium uppercase tracking-wide text-command-tertiary">{title}</p>
          <p className="mt-2 text-2xl font-semibold tabular-nums text-command-text">{value}</p>
          <p className="mt-1 text-sm text-command-secondary">{subtitle}</p>
        </div>
        <span className={`rounded-xl p-2.5 ${iconBgClass}`}>
          <Icon className={`h-5 w-5 ${iconClass}`} />
        </span>
      </div>
    </CommandCard>
  );
}
