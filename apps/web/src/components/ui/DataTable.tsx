"use client";

import { useMemo, useState, type ReactNode } from "react";

import { cn } from "@/src/lib/cn";

import { EmptyState } from "./EmptyState";

export type DataTableColumn<T> = {
  id: string;
  header: string;
  sortable?: boolean;
  render: (row: T) => ReactNode;
  className?: string;
};

type Props<T> = {
  columns: Array<DataTableColumn<T>>;
  rows: T[];
  rowKey: (row: T) => string;
  loading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  pageSize?: number;
};

export function DataTable<T>({
  columns,
  rows,
  rowKey,
  loading,
  emptyTitle = "No data",
  emptyDescription,
  pageSize = 10,
}: Props<T>) {
  const [sortCol, setSortCol] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [page, setPage] = useState(0);

  const sorted = useMemo(() => {
    if (!sortCol) return rows;
    return [...rows];
  }, [rows, sortCol, sortDir]);

  const pageCount = Math.max(1, Math.ceil(sorted.length / pageSize));
  const pageRows = sorted.slice(page * pageSize, (page + 1) * pageSize);

  if (loading) {
    return (
      <div className="overflow-hidden rounded-xl border border-border bg-card">
        {[0, 1, 2].map((i) => (
          <div key={i} className="flex gap-4 border-b border-border px-4 py-3 last:border-0">
            <div className="h-4 w-full animate-pulse rounded bg-muted" />
          </div>
        ))}
      </div>
    );
  }

  if (rows.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="space-y-3">
      <div className="hidden overflow-x-auto rounded-xl border border-border md:block">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-muted/40 text-xs uppercase text-muted-foreground">
            <tr>
              {columns.map((col) => (
                <th key={col.id} className={cn("px-4 py-3", col.className)}>
                  {col.sortable ? (
                    <button
                      type="button"
                      className="font-medium hover:text-foreground"
                      onClick={() => {
                        if (sortCol === col.id) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
                        else {
                          setSortCol(col.id);
                          setSortDir("asc");
                        }
                      }}
                    >
                      {col.header}
                    </button>
                  ) : (
                    col.header
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row) => (
              <tr key={rowKey(row)} className="border-t border-border">
                {columns.map((col) => (
                  <td key={col.id} className={cn("px-4 py-3 text-foreground", col.className)}>
                    {col.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="space-y-2 md:hidden">
        {pageRows.map((row) => (
          <div key={rowKey(row)} className="rounded-lg border border-border bg-card p-3 shadow-sm">
            {columns.map((col) => (
              <div key={col.id} className="flex justify-between gap-3 py-1 text-sm">
                <span className="text-muted-foreground">{col.header}</span>
                <span className="text-foreground">{col.render(row)}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      {pageCount > 1 ? (
        <div className="flex items-center justify-center gap-2 text-sm">
          <button
            type="button"
            className="rounded border border-border px-3 py-1 disabled:opacity-40"
            disabled={page === 0}
            onClick={() => setPage((p) => p - 1)}
          >
            Prev
          </button>
          <span className="text-muted-foreground">
            Page {page + 1} / {pageCount}
          </span>
          <button
            type="button"
            className="rounded border border-border px-3 py-1 disabled:opacity-40"
            disabled={page + 1 >= pageCount}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </button>
        </div>
      ) : null}
    </div>
  );
}
