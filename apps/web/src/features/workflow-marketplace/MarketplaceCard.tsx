"use client";

import Link from "next/link";

import type { WorkflowTemplateRecord } from "@/lib/api/workflowMarketplace";

function Stars({ value }: { value: number }) {
  const full = Math.round(value);
  return (
    <span className="shrink-0 text-amber-500" aria-label={`Rating ${value}`}>
      {"★".repeat(full)}
      {"☆".repeat(5 - full)}
    </span>
  );
}

function categoryIcon(category: string): string {
  const map: Record<string, string> = {
    irrigation: "💧",
    pest: "🐛",
    greenhouse: "🌿",
    livestock: "🐄",
    general: "⚙️",
    aquaponics: "🐟",
    energy: "⚡",
    report: "📊",
  };
  return map[category] ?? "📦";
}

type Props = {
  template: WorkflowTemplateRecord;
};

export function MarketplaceCard({ template: t }: Props) {
  return (
    <Link
      href={`/marketplace/${t.id}`}
      className="group flex h-full min-h-[200px] min-w-0 flex-col gap-3 rounded-lg border border-stone-200 bg-white p-4 shadow-sm transition hover:border-stone-400 hover:shadow-md"
    >
      <div className="flex min-w-0 items-start gap-2">
        <span className="shrink-0 text-2xl leading-none" aria-hidden>
          {categoryIcon(t.category)}
        </span>
        <h3 className="min-w-0 flex-1 truncate text-base font-semibold text-stone-900 group-hover:text-stone-950">
          {t.name}
        </h3>
      </div>
      <p className="min-w-0 flex-1 text-sm leading-snug text-stone-600 line-clamp-3">{t.description}</p>
      <div className="mt-auto flex min-w-0 items-center justify-between gap-2 border-t border-stone-100 pt-3 text-xs text-stone-500">
        <span className="truncate">{t.downloads_count} downloads</span>
        <Stars value={t.rating_avg} />
      </div>
      <p className="min-w-0 truncate text-[10px] text-stone-400">by {t.author_tenant_id.slice(0, 8)}…</p>
    </Link>
  );
}
