"use client";

import { Search } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { HQ_NAV_SECTIONS } from "@/lib/hq/nav-config";

type CommandPaletteProps = {
  open: boolean;
  onClose: () => void;
};

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const items = useMemo(() => HQ_NAV_SECTIONS.flatMap((s) => s.items), []);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const filtered = items.filter((i) => i.label.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/30 px-4 pt-24" role="dialog" aria-label="Command palette">
      <div className="w-full max-w-lg rounded-2xl border border-cream-border bg-white shadow-card-md">
        <div className="flex items-center gap-2 border-b border-cream-border px-4 py-3">
          <Search className="h-4 w-4 text-ink-tertiary" />
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Jump to…"
            className="w-full bg-transparent text-sm outline-none"
            aria-label="Search navigation"
          />
          <kbd className="rounded border border-cream-border px-1.5 text-[10px] text-ink-tertiary">Esc</kbd>
        </div>
        <ul className="max-h-64 overflow-y-auto p-2">
          {filtered.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                onClick={onClose}
                className="block rounded-lg px-3 py-2 text-sm hover:bg-cream-muted"
              >
                {item.label}
                <span className="ml-2 text-xs text-ink-tertiary">{item.href}</span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
