"use client";

import type { ReactNode } from "react";

export type AdminColumn<T> = {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  className?: string;
};

type AdminDataTableProps<T> = {
  columns: AdminColumn<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  dense?: boolean;
  onRowContextMenu?: (row: T, event: React.MouseEvent) => void;
};

export function AdminDataTable<T>({ columns, rows, rowKey, dense, onRowContextMenu }: AdminDataTableProps<T>) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <table className="min-w-full text-left text-sm">
        <thead className="sticky top-0 z-[1] border-b border-slate-200 bg-slate-100 text-xs uppercase text-slate-500 dark:bg-slate-800">
          <tr>
            {columns.map((col) => (
              <th key={col.key} className={`px-4 py-3 ${col.className ?? ""}`}>{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={rowKey(row)}
              className={`border-b border-slate-100 hover:bg-blue-50/60 dark:border-slate-800 dark:hover:bg-slate-800/80 ${dense ? "" : ""}`}
              onContextMenu={onRowContextMenu ? (e) => onRowContextMenu(row, e) : undefined}
            >
              {columns.map((col) => (
                <td key={col.key} className={`px-4 py-2.5 ${col.className ?? ""}`}>{col.render(row)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
