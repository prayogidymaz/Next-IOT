"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { listMarketplaceTemplates, type WorkflowTemplateRecord } from "@/lib/api/workflowMarketplace";

import { MarketplaceCard } from "./MarketplaceCard";

const CATEGORIES = ["", "irrigation", "pest", "greenhouse", "livestock", "general"] as const;

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
    <div className="mx-auto w-full max-w-7xl p-4 md:p-6">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        <aside className="w-full shrink-0 space-y-4 rounded-xl border border-stone-200 bg-white p-4 lg:sticky lg:top-4 lg:w-64">
          <h2 className="text-sm font-semibold text-stone-800">Filters</h2>
          <label className="block text-xs text-stone-600">
            Category
            <select
              className="mt-1 w-full rounded border border-stone-300 px-2 py-1.5 text-sm"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              {CATEGORIES.map((c) => (
                <option key={c || "all"} value={c}>
                  {c || "All"}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-xs text-stone-600">
            Locale
            <input
              className="mt-1 w-full rounded border border-stone-300 px-2 py-1.5 text-sm"
              value={locale}
              onChange={(e) => setLocale(e.target.value)}
              placeholder="id, en…"
            />
          </label>
          <label className="block text-xs text-stone-600">
            Sort by
            <select
              className="mt-1 w-full rounded border border-stone-300 px-2 py-1.5 text-sm"
              value={sort}
              onChange={(e) => setSort(e.target.value)}
            >
              <option value="downloads">Downloads</option>
              <option value="rating">Rating</option>
              <option value="newest">Newest</option>
            </select>
          </label>
        </aside>

        <main className="min-w-0 flex-1">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h1 className="text-2xl font-semibold text-stone-900">Template marketplace</h1>
            <input
              className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm sm:max-w-xs"
              placeholder="Search templates…"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(0);
              }}
            />
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {pageItems.map((t) => (
              <div key={t.id} className="min-w-0">
                <MarketplaceCard template={t} />
              </div>
            ))}
          </div>

          {pageItems.length === 0 ? (
            <p className="mt-6 text-center text-sm text-stone-500">No templates match your filters.</p>
          ) : null}

          <div className="mt-6 flex items-center justify-center gap-2">
            <button
              type="button"
              className="rounded border border-stone-300 px-3 py-1 text-sm disabled:opacity-40"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
            >
              Prev
            </button>
            <span className="text-sm text-stone-600">
              Page {page + 1} / {pageCount}
            </span>
            <button
              type="button"
              className="rounded border border-stone-300 px-3 py-1 text-sm disabled:opacity-40"
              disabled={page + 1 >= pageCount}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}
