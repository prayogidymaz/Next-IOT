"use client";

import { StatCard as UiStatCard } from "@next-iot/ui";
import type { LucideIcon } from "lucide-react";

type StatCardProps = {
  title: string;
  value: string;
  subtitle?: string;
  trend?: { direction: "up" | "down"; label: string };
  icon: LucideIcon;
};

export function StatCard({ title, value, subtitle, trend, icon: Icon }: StatCardProps) {
  return (
    <UiStatCard
      title={title}
      value={value}
      subtitle={subtitle}
      trend={trend}
      icon={<Icon className="h-5 w-5" />}
    />
  );
}
