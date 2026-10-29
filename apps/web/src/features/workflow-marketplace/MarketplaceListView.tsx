"use client";

import { Filter } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { listMarketplaceTemplates, type WorkflowTemplateRecord } from "@/lib/api/workflowMarketplace";

import { MarketplaceCard } from "./MarketplaceCard";

const CATEGORIES = ["", "irrigation", "pest", "greenhouse", "livestock", "general"] as const;

function filterAsideClass(showFilters: boolean): string {
  const base = "w-full shrink-0 lg:w-64";
  if (showFilters) return `${base} block`;
  return `${base} hidden lg:block`;
}

export function MarketplaceListView() {
  const [items, setItems] = useState<WorkflowTemplateRecord[]>([]);
  const [category, setCategory] = useState<string>("");
  const [locale, setLocale] = useState("");
  const [sort, setSort] = useState("downloads");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
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
    <div className="p-6">
      <div className="mb-4 lg:hidden">
        <Button
          variant="outline"
          onClick={() => setShowFilters((open) => !open)}
          className="w-full justify-start gap-2"
          aria-expanded={showFilters}
        >
          <Filter className="h-4 w-4 shrink-0" aria-hidden />
          {showFilters ? "Hide filters" : "Show filters"}
        </Button>
      </div>

      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        <aside className={filterAsideClass(showFilters)}>
          <div className="space-y-4 rounded-lg border border-stone-200 bg-white p-4">
            <h3 className="text-sm font-semibold text-stone-900">Filters</h3>
            <div className="space-y-2">
              <label htmlFor="marketplace-category" className="text-sm font-medium text-stone-700">
                Category
              </label>
              <select
                id="marketplace-category"
                className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                {CATEGORIES.map((c) => (
                  <option key={c || "all"} value={c}>
                    {c || "All"}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label htmlFor="marketplace-locale" className="text-sm font-medium text-stone-700">
                Locale
              </label>
              <input
                id="marketplace-locale"
                className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm"
                value={locale}
                onChange={(e) => setLocale(e.target.value)}
                placeholder="id, en…"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="marketplace-sort" className="text-sm font-medium text-stone-700">
                Sort by
              </label>
              <select
                id="marketplace-sort"
                className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm"
                value={sort}
                onChange={(e) => setSort(e.target.value)}
              >
                <option value="downloads">Downloads</option>
                <option value="rating">Rating</option>
                <option value="newest">Recent</option>
              </select>
            </div>
          </div>
        </aside>

        <main className="min-w-0 flex-1 space-y-4">
          <h1 className="text-2xl font-bold text-stone-900">Template marketplace</h1>
          <input
            className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm"
            placeholder="Search templates…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
          />

          <div className="grid w-full grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {pageItems.map((t) => (
              <MarketplaceCard key={t.id} template={t} />
            ))}
          </div>

          {pageItems.length === 0 ? (
            <p className="text-center text-sm text-stone-500">No templates match your filters.</p>
          ) : null}

          <div className="flex items-center justify-center gap-2 pt-2">
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
