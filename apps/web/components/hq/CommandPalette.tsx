"use client";

import { Search } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";

import { listAlarms } from "@/lib/api/alarms";
import { listDevices } from "@/lib/api/devices";
import { listMeshWorkflows } from "@/lib/api/meshWorkflows";
import { listTenantMembers } from "@/lib/api/tenantMembers";
import { listMarketplaceTemplates } from "@/lib/api/workflowMarketplace";
import { fetchAuthMe } from "@/lib/auth/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";
import { HQ_NAV_SECTIONS } from "@/lib/hq/nav-config";

type CommandPaletteProps = {
  open: boolean;
  onClose: () => void;
};

type SearchHit = {
  category: string;
  label: string;
  href: string;
  meta?: string;
};

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [apiHits, setApiHits] = useState<SearchHit[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<number | null>(null);

  const navItems = useMemo(() => HQ_NAV_SECTIONS.flatMap((s) => s.items), []);

  useEffect(() => {
    if (!open) {
      setQuery("");
      setApiHits([]);
      return;
    }
    inputRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  useEffect(() => {
    if (!open) return;
    const q = query.trim();
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    if (q.length < 2) {
      setApiHits([]);
      return;
    }
    debounceRef.current = window.setTimeout(() => {
      void (async () => {
        const token = readAccessTokenFromDocument();
        const hits: SearchHit[] = [];
        try {
          const [devices, alarms, workflows, templates] = await Promise.all([
            listDevices().then((rows) =>
              rows
                .filter((d) => d.name.toLowerCase().includes(q.toLowerCase()))
                .slice(0, 4)
                .map((d) => ({ category: "Devices", label: d.name, href: `/devices/${d.id}`, meta: d.device_type })),
            ),
            listAlarms({ status: "active", search: q }).then((rows) =>
              rows.slice(0, 4).map((a) => ({ category: "Alarms", label: a.title, href: "/alarms", meta: a.severity })),
            ),
            listMeshWorkflows({ search: q }).then((rows) =>
              rows.slice(0, 4).map((w) => ({ category: "Workflows", label: w.name, href: `/workflows/${w.id}` })),
            ),
            listMarketplaceTemplates({ sort: "downloads", limit: 20, search: q }).then((rows) =>
              rows.slice(0, 4).map((t) => ({ category: "Templates", label: t.name, href: `/marketplace/${t.id}` })),
            ),
          ]);
          hits.push(...devices, ...alarms, ...workflows, ...templates);
          if (token) {
            const me = await fetchAuthMe(token);
            const members = await listTenantMembers(me.tenant_id, q);
            hits.push(
              ...members.slice(0, 4).map((m) => ({
                category: "Members",
                label: m.email,
                href: "/members",
                meta: m.role,
              })),
            );
          }
        } catch {
          /* ignore partial search failures */
        }
        setApiHits(hits);
      })();
    }, 300);
    return () => {
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
    };
  }, [query, open]);

  if (!open) return null;

  const navFiltered = navItems
    .filter((i) => i.label.toLowerCase().includes(query.toLowerCase()) || i.href.includes(query.toLowerCase()))
    .map(
      (i): SearchHit => ({
        category: "Navigation",
        label: i.label,
        href: i.href,
        meta: i.href,
      }),
    );

  const grouped = [...navFiltered, ...apiHits].reduce<Record<string, SearchHit[]>>((acc, hit) => {
    acc[hit.category] = acc[hit.category] ? [...acc[hit.category], hit] : [hit];
    return acc;
  }, {});

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 px-4 pt-24"
      role="dialog"
      aria-label="Command palette"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="w-full max-w-lg rounded-2xl border border-border bg-card text-foreground shadow-lg">
        <div className="flex items-center gap-2 border-b border-border px-4 py-3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search pages, devices, alarms, workflows…"
            className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
            aria-label="Search"
          />
          <kbd className="rounded border border-border px-1.5 text-[10px] text-muted-foreground">Esc</kbd>
        </div>
        <ul className="max-h-80 overflow-y-auto p-2">
          {Object.keys(grouped).length === 0 ? (
            <li className="px-3 py-2 text-sm text-muted-foreground">No matches</li>
          ) : (
            Object.entries(grouped).map(([category, items]) => (
              <li key={category} className="mb-2">
                <p className="px-3 py-1 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">{category}</p>
                {items.map((item) => (
                  <Link key={`${category}-${item.href}-${item.label}`} href={item.href} onClick={onClose} className="block rounded-lg px-3 py-2 text-sm hover:bg-muted">
                    <span className="font-medium">{item.label}</span>
                    {item.meta ? <span className="ml-2 text-xs text-muted-foreground">{item.meta}</span> : null}
                  </Link>
                ))}
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}
