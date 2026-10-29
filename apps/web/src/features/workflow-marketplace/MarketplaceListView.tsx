"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { listMarketplaceTemplates, type WorkflowTemplateRecord } from "@/lib/api/workflowMarketplace";

import { MarketplaceCard } from "./MarketplaceCard";

const CATEGORIES = [
  { value: "", label: "All" },
  { value: "irrigation", label: "Irrigation" },
  { value: "pest", label: "Pest" },
  { value: "greenhouse", label: "Greenhouse" },
  { value: "aquaponics", label: "Aquaponics" },
  { value: "energy", label: "Energy" },
  { value: "report", label: "Report" },
  { value: "livestock", label: "Livestock" },
  { value: "general", label: "General" },
] as const;

const compactSelectClass =
  "h-8 shrink-0 rounded-lg border border-stone-300 bg-white px-2 text-xs text-stone-800";

const desktopSelectClass = "h-9 w-full rounded-lg border border-stone-300 bg-white px-2 text-sm";

type FilterControlsProps = {
  category: string;
  sort: string;
  onCategory: (value: string) => void;
  onSort: (value: string) => void;
  idPrefix: string;
  compact?: boolean;
};

function FilterControls({ category, sort, onCategory, onSort, idPrefix, compact = false }: FilterControlsProps) {
  const selectClass = compact ? compactSelectClass : desktopSelectClass;
  const labelClass = compact ? "sr-only" : "text-xs font-medium text-stone-500";

  return (
    <>
      <div className={compact ? "" : "space-y-1.5"}>
        <label htmlFor={`${idPrefix}-category`} className={labelClass}>
          Category
        </label>
        <select
          id={`${idPrefix}-category`}
          className={compact ? `${selectClass} min-w-[7.5rem]` : selectClass}
          value={category}
          onChange={(e) => onCategory(e.target.value)}
          aria-label="Category"
        >
          {CATEGORIES.map((c) => (
            <option key={c.value || "all"} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
      </div>
      <div className={compact ? "" : "space-y-1.5"}>
        <label htmlFor={`${idPrefix}-sort`} className={labelClass}>
          Sort by
        </label>
        <select
          id={`${idPrefix}-sort`}
          className={compact ? `${selectClass} min-w-[6.5rem]` : selectClass}
          value={sort}
          onChange={(e) => onSort(e.target.value)}
          aria-label="Sort by"
        >
          <option value="downloads">Downloads</option>
          <option value="rating">Rating</option>
          <option value="newest">Recent</option>
        </select>
      </div>
    </>
  );
}

export function MarketplaceListView() {
  const [items, setItems] = useState<WorkflowTemplateRecord[]>([]);
  const [category, setCategory] = useState<string>("");
  const [sort, setSort] = useState("downloads");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const pageSize = 9;

  const load = useCallback(async () => {
    const list = await listMarketplaceTemplates({
      category: category || undefined,
      sort,
      limit: 100,
    });
    setItems(list);
  }, [category, sort]);

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

  function resetFilters() {
    setCategory("");
    setSort("downloads");
    setPage(0);
  }

  return (
    <div className="p-6">
      <h1 className="mb-6 text-2xl font-bold text-stone-900">Template marketplace</h1>

      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        <aside className="hidden w-60 shrink-0 lg:block">
          <div className="sticky top-6 space-y-3 rounded-lg border border-stone-200 bg-white p-4">
            <h3 className="text-sm font-semibold text-stone-900">Filters</h3>
            <FilterControls
              idPrefix="desktop"
              category={category}
              sort={sort}
              onCategory={(v) => {
                setCategory(v);
                setPage(0);
              }}
              onSort={(v) => {
                setSort(v);
                setPage(0);
              }}
            />
            <Button variant="ghost" size="sm" className="mt-1 w-full" onClick={resetFilters}>
              Reset filters
            </Button>
          </div>
        </aside>

        <div className="min-w-0 flex-1 space-y-4">
          <div className="flex gap-2 overflow-x-auto pb-1 lg:hidden">
            <FilterControls
              idPrefix="mobile"
              compact
              category={category}
              sort={sort}
              onCategory={(v) => {
                setCategory(v);
                setPage(0);
              }}
              onSort={(v) => {
                setSort(v);
                setPage(0);
              }}
            />
          </div>

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
        </div>
      </div>
    </div>
  );
}
