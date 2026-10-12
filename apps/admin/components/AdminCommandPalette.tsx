"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { ALL_NAV_ITEMS } from "@/lib/admin-nav";

type AdminCommandPaletteProps = {
  open: boolean;
  onClose: () => void;
  onFocusSearch: () => void;
};

export function AdminCommandPalette({ open, onClose, onFocusSearch }: AdminCommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");

  const go = useCallback(
    (href: string) => {
      router.push(href);
      onClose();
      setQuery("");
    },
    [router, onClose],
  );

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (open) onClose();
      }
      if (e.key === "/" && !open && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        onFocusSearch();
      }
      if (!mod) return;
      if (e.key.toLowerCase() === "t" && e.shiftKey === false) {
        const seq = (window as Window & { __adminKeySeq?: string }).__adminKeySeq;
        if (seq === "g") {
          e.preventDefault();
          go("/tenants");
          (window as Window & { __adminKeySeq?: string }).__adminKeySeq = "";
        }
      }
    };
    const trackG = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() === "g" && !e.metaKey && !e.ctrlKey) {
        (window as Window & { __adminKeySeq?: string }).__adminKeySeq = "g";
        window.setTimeout(() => {
          (window as Window & { __adminKeySeq?: string }).__adminKeySeq = "";
        }, 800);
      }
      if (e.key.toLowerCase() === "t" && (window as Window & { __adminKeySeq?: string }).__adminKeySeq === "g") {
        e.preventDefault();
        go("/tenants");
      }
      if (e.key.toLowerCase() === "b" && (window as Window & { __adminKeySeq?: string }).__adminKeySeq === "g") {
        e.preventDefault();
        go("/billing");
      }
      if (e.key.toLowerCase() === "a" && (window as Window & { __adminKeySeq?: string }).__adminKeySeq === "n") {
        e.preventDefault();
        go("/announcements");
      }
      if (e.key.toLowerCase() === "n" && !e.metaKey) {
        (window as Window & { __adminKeySeq?: string }).__adminKeySeq = "n";
        window.setTimeout(() => {
          const seq = (window as Window & { __adminKeySeq?: string }).__adminKeySeq;
          if (seq === "n") (window as Window & { __adminKeySeq?: string }).__adminKeySeq = "";
        }, 800);
      }
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("keydown", trackG);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("keydown", trackG);
    };
  }, [open, onClose, go, onFocusSearch]);

  if (!open) return null;

  const filtered = ALL_NAV_ITEMS.filter((item) =>
    item.label.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-slate-900/40 p-4 pt-24" role="dialog" aria-modal="true">
      <div className="w-full max-w-lg rounded-xl border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900">
        <input
          autoFocus
          className="w-full border-b border-slate-200 px-4 py-3 text-sm outline-none dark:border-slate-700"
          placeholder="Jump to page… (⌘K)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <ul className="max-h-80 overflow-auto p-2">
          {filtered.map((item) => (
            <li key={item.href}>
              <button
                type="button"
                className="flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm hover:bg-slate-100 dark:hover:bg-slate-800"
                onClick={() => go(item.href)}
              >
                <span>{item.label}</span>
                {item.shortcut ? <kbd className="text-[10px] text-slate-400">{item.shortcut}</kbd> : null}
              </button>
            </li>
          ))}
        </ul>
      </div>
      <button type="button" className="fixed inset-0 -z-10" aria-label="Close" onClick={onClose} />
    </div>
  );
}
