"use client";

import Link from "next/link";

import type { WorkflowTemplateRecord } from "@/lib/api/workflowMarketplace";

function RatingStars({ value }: { value: number }) {
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

function TagBadge({ tag }: { tag: string }) {
  return (
    <span className="rounded-full border border-stone-200 bg-stone-50 px-2 py-0.5 text-[10px] font-medium text-stone-600">
      {tag}
    </span>
  );
}

type Props = {
  template: WorkflowTemplateRecord;
};

export function MarketplaceCard({ template: t }: Props) {
  const tags = t.tags_json.slice(0, 3);

  return (
    <Link href={`/marketplace/${t.id}`} className="block h-full min-w-0 text-inherit no-underline">
      <article className="flex h-full min-h-[220px] flex-col gap-3 rounded-lg border border-stone-200 bg-white p-4 shadow-sm transition hover:border-stone-400 hover:shadow-md">
        <div className="flex min-w-0 items-start gap-2">
          <span className="shrink-0 text-2xl leading-none" aria-hidden>
            {categoryIcon(t.category)}
          </span>
          <h3 className="min-w-0 flex-1 truncate text-base font-semibold text-stone-900">{t.name}</h3>
        </div>
        <p className="min-w-0 text-sm leading-snug text-stone-600 line-clamp-3">{t.description}</p>
        {tags.length > 0 ? (
          <div className="flex min-w-0 flex-wrap gap-1">
            {tags.map((tag) => (
              <TagBadge key={tag} tag={tag} />
            ))}
          </div>
        ) : (
          <div className="h-0" aria-hidden />
        )}
        <div className="mt-auto flex min-w-0 items-center justify-between gap-2 text-xs text-stone-500">
          <span className="truncate">{t.downloads_count} downloads</span>
          <RatingStars value={t.rating_avg} />
        </div>
      </article>
    </Link>
  );
}
