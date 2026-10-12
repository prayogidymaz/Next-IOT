"use client";

import { AdminCard } from "@/components/ui/AdminCard";

export function AdminPlaceholder({ title, description }: { title: string; description: string }) {
  return (
    <AdminCard className="p-6">
      <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h2>
      <p className="mt-2 text-sm text-slate-500">{description}</p>
    </AdminCard>
  );
}
