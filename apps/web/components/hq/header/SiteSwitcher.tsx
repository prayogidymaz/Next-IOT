"use client";

import { useEffect, useState } from "react";

import { listSites, type SiteRecord } from "@/lib/api/sites";

const STORAGE_KEY = "hq_active_site_id";

export function SiteSwitcher() {
  const [sites, setSites] = useState<SiteRecord[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) setActiveId(stored);
    void listSites()
      .then((rows) => {
        setSites(rows);
        if (!stored && rows[0]) {
          setActiveId(rows[0].id);
          localStorage.setItem(STORAGE_KEY, rows[0].id);
        }
      })
      .catch(() => setSites([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading || sites.length === 0) return null;

  return (
    <label className="hidden min-w-0 items-center gap-2 lg:flex">
      <span className="sr-only">Active site</span>
      <select
        value={activeId}
        onChange={(e) => {
          setActiveId(e.target.value);
          localStorage.setItem(STORAGE_KEY, e.target.value);
        }}
        className="max-w-[10rem] truncate rounded-lg border border-border bg-card px-2 py-1.5 text-xs text-foreground"
        aria-label="Active site"
      >
        {sites.map((s) => (
          <option key={s.id} value={s.id}>
            {s.name}
          </option>
        ))}
      </select>
    </label>
  );
}

export function readActiveSiteId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(STORAGE_KEY);
}
