"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { listMarketplaceTemplates, type WorkflowTemplateRecord } from "@/lib/api/workflowMarketplace";

const CATEGORIES = ["", "irrigation", "pest", "greenhouse", "livestock", "general"] as const;

function Stars({ value }: { value: number }) {
  const full = Math.round(value);
  return (
    <span className="text-amber-500" aria-label={`Rating ${value}`}>
      {"★".repeat(full)}
      {"☆".repeat(5 - full)}
    </span>
  );
}

function categoryIcon(category: string): string {
  const map: Record<string, string> = { irrigation: "💧", pest: "🐛", greenhouse: "🌿", livestock: "🐄", general: "⚙️" };
  return map[category] ?? "📦";
}

export function MarketplaceListView() {
  const [items, setItems] = useState<WorkflowTemplateRecord[]>([]);
  const [category, setCategory] = useState<string>("");
  const [locale, setLocale] = useState("");
  const [sort, setSort] = useState("downloads");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const pageSize = 9;

  const load = useCallback(async () => {
    const list = await listMarketplaceTemplates({
      category: category || undefined,
      locale: locale || undefined,
      sort,
      limit: 100,
    });
    setItems(list);
  }, [category, locale, sort]);

  useEffect(() => {
    void load().catch(() => setItems([]));
  }, [load]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return items;
    return items.filter((t) => t.name.toLowerCase().includes(q) || t.description.toLowerCase().includes(q));
  }, [items, search]);

  const pageItems = filtered.slice(page * pageSize, (page + 1) * pageSize);
  const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));

  return (
    <div className="flex flex-col gap-6 p-6 lg:flex-row">
      <aside className="w-full shrink-0 space-y-4 rounded-xl border border-stone-200 bg-white p-4 lg:w-56">
        <h2 className="text-sm font-semibold text-stone-800">Filters</h2>
        <label className="block text-xs text-stone-600">
          Category
          <select className="mt-1 w-full rounded border px-2 py-1.5 text-sm" value={category} onChange={(e) => setCategory(e.target.value)}>
            {CATEGORIES.map((c) => (
              <option key={c || "all"} value={c}>
                {c || "All"}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-xs text-stone-600">
          Locale
          <input className="mt-1 w-full rounded border px-2 py-1.5 text-sm" value={locale} onChange={(e) => setLocale(e.target.value)} placeholder="id, en…" />
        </label>
        <label className="block text-xs text-stone-600">
          Sort by
          <select className="mt-1 w-full rounded border px-2 py-1.5 text-sm" value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="downloads">Downloads</option>
            <option value="rating">Rating</option>
            <option value="newest">Newest</option>
          </select>
        </label>
      </aside>

      <div className="min-w-0 flex-1 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-2xl font-semibold text-stone-900">Template marketplace</h1>
          <input
            className="rounded-lg border border-stone-300 px-3 py-2 text-sm"
            placeholder="Search templates…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {pageItems.map((t) => (
            <Link
              key={t.id}
              href={`/marketplace/${t.id}`}
              className="flex flex-col rounded-xl border border-stone-200 bg-white p-4 shadow-sm transition hover:border-stone-400"
            >
              <span className="text-2xl">{categoryIcon(t.category)}</span>
              <h3 className="mt-2 font-medium text-stone-900">{t.name}</h3>
              <p className="mt-1 line-clamp-2 text-xs text-stone-600">{t.description}</p>
              <div className="mt-auto flex items-center justify-between pt-3 text-xs text-stone-500">
                <span>{t.downloads_count} downloads</span>
                <Stars value={t.rating_avg} />
              </div>
              <p className="mt-1 truncate text-[10px] text-stone-400">by {t.author_tenant_id.slice(0, 8)}…</p>
            </Link>
          ))}
        </div>
        <div className="flex items-center justify-center gap-2">
          <button type="button" className="rounded border px-3 py-1 text-sm disabled:opacity-40" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>
            Prev
          </button>
          <span className="text-sm text-stone-600">
            Page {page + 1} / {pageCount}
          </span>
          <button
            type="button"
            className="rounded border px-3 py-1 text-sm disabled:opacity-40"
            disabled={page + 1 >= pageCount}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
