"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { listMarketplaceTemplates, type WorkflowTemplateRecord } from "@/lib/api/workflowMarketplace";

import { GridSkeleton } from "@/src/components/LoadingSkeleton";

import { marketplaceLocaleParam, readClientLocale } from "@/lib/i18n/readClientLocale";

import { MarketplaceCard } from "./MarketplaceCard";

const LOCALES = [
  { value: "", label: "All languages" },
  { value: "id", label: "Indonesian" },
  { value: "en", label: "English" },
  { value: "zh-CN", label: "Chinese (Simplified)" },
] as const;

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
  "h-8 shrink-0 rounded-lg border border-border bg-card px-2 text-xs text-foreground";

const desktopSelectClass = "h-9 w-full rounded-lg border border-border bg-card px-2 text-sm text-foreground";

type FilterControlsProps = {
  category: string;
  sort: string;
  locale: string;
  onCategory: (value: string) => void;
  onSort: (value: string) => void;
  onLocale: (value: string) => void;
  idPrefix: string;
  compact?: boolean;
};

function FilterControls({ category, sort, locale, onCategory, onSort, onLocale, idPrefix, compact = false }: FilterControlsProps) {
  const selectClass = compact ? compactSelectClass : desktopSelectClass;
  const labelClass = compact ? "sr-only" : "text-xs font-medium text-muted-foreground";

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
        <label htmlFor={`${idPrefix}-locale`} className={labelClass}>
          Language
        </label>
        <select
          id={`${idPrefix}-locale`}
          className={compact ? `${selectClass} min-w-[7rem]` : selectClass}
          value={locale}
          onChange={(e) => onLocale(e.target.value)}
          aria-label="Language"
        >
          {LOCALES.map((l) => (
            <option key={l.value || "all"} value={l.value}>
              {l.label}
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
  const [locale, setLocale] = useState(() => marketplaceLocaleParam(readClientLocale()));
  const [sort, setSort] = useState("downloads");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const pageSize = 9;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const list = await listMarketplaceTemplates({
        category: category || undefined,
        locale: locale || undefined,
        sort,
        limit: 100,
      });
      setItems(list);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [category, locale, sort]);

  useEffect(() => {
    void load();
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
    setLocale(marketplaceLocaleParam(readClientLocale()));
    setSort("downloads");
    setPage(0);
  }

  return (
    <div>
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        <aside className="hidden w-60 shrink-0 lg:block">
          <div className="sticky top-6 space-y-3 rounded-lg border border-border bg-card p-4">
            <h3 className="text-sm font-semibold text-foreground">Filters</h3>
            <FilterControls
              idPrefix="desktop"
              category={category}
              sort={sort}
              locale={locale}
              onCategory={(v) => {
                setCategory(v);
                setPage(0);
              }}
              onSort={(v) => {
                setSort(v);
                setPage(0);
              }}
              onLocale={(v) => {
                setLocale(v);
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
              locale={locale}
              onCategory={(v) => {
                setCategory(v);
                setPage(0);
              }}
              onSort={(v) => {
                setSort(v);
                setPage(0);
              }}
              onLocale={(v) => {
                setLocale(v);
                setPage(0);
              }}
            />
          </div>

          <input
            className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground"
            placeholder="Search templates…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
          />

          {loading ? (
            <GridSkeleton count={6} />
          ) : (
            <div className="grid w-full grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {pageItems.map((t) => (
                <MarketplaceCard key={t.id} template={t} />
              ))}
            </div>
          )}

          {pageItems.length === 0 ? (
            <p className="text-center text-sm text-muted-foreground">No templates match your filters.</p>
          ) : null}

          <div className="flex items-center justify-center gap-2 pt-2">
            <button
              type="button"
              className="rounded-lg border border-border bg-card px-3 py-1 text-sm text-foreground disabled:opacity-40"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
            >
              Prev
            </button>
            <span className="text-sm text-muted-foreground">
              Page {page + 1} / {pageCount}
            </span>
            <button
              type="button"
              className="rounded-lg border border-border bg-card px-3 py-1 text-sm text-foreground disabled:opacity-40"
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
