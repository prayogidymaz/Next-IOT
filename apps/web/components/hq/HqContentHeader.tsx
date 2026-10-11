"use client";

import { Bell, ChevronRight, Search } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { CommandPalette } from "@/components/hq/CommandPalette";
import { HQ_DOMAINS, type HqDomainId } from "@/lib/hq/domains";
import { titleForPath } from "@/lib/hq/nav-config";
import { useHqShell } from "@/lib/hq/hq-shell-context";
import { useTenantRealtime } from "@/hooks/useTenantRealtime";

export function HqContentHeader() {
  const pathname = usePathname();
  const { domainId, setDomainId, notificationCount, systemHealth } = useHqShell();
  const { connection } = useTenantRealtime();
  const title = titleForPath(pathname);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [themeDark, setThemeDark] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", themeDark);
  }, [themeDark]);

  const linkStatus =
    connection === "connected" ? "Connected" : connection === "degraded" ? "Degraded" : "Connecting…";

  return (
    <>
      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
      <header className="sticky top-0 z-10 border-b border-cream-border bg-cream-page/95 px-6 py-4 backdrop-blur-md">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <nav className="mb-1 flex items-center gap-1 text-xs text-ink-tertiary" aria-label="Breadcrumb">
              <Link href="/dashboard" className="hover:text-ink-secondary">
                Web HQ
              </Link>
              <ChevronRight className="h-3 w-3" />
              <span className="text-ink-secondary">{title}</span>
            </nav>
            <h1 className="text-xl font-semibold tracking-tight text-ink-primary md:text-2xl">{title}</h1>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => setPaletteOpen(true)}
              className="hq-pill hidden text-xs sm:inline-flex"
              aria-label="Open command palette"
            >
              <Search className="h-3.5 w-3.5" />
              Quick search
              <kbd className="font-mono text-[10px] text-ink-tertiary">⌘K</kbd>
            </button>
            <div className="flex flex-wrap gap-1.5">
              {HQ_DOMAINS.map((d) => {
                const active = d.id === domainId;
                return (
                  <button
                    key={d.id}
                    type="button"
                    onClick={() => setDomainId(d.id as HqDomainId)}
                    className={`rounded-full border px-2.5 py-1 text-xs font-medium transition ${
                      active
                        ? `${d.softClass} border-cream-border shadow-sm`
                        : "border-cream-border bg-white text-ink-secondary hover:bg-cream-muted"
                    }`}
                  >
                    {d.emoji} {!active ? d.label.split(" ")[0] : d.label}
                  </button>
                );
              })}
            </div>
            <span className="hq-pill text-xs font-medium font-mono text-accent-cobalt">
              <span
                className={`h-2 w-2 rounded-full ${
                  connection === "connected" ? "bg-accent-emerald animate-pulse" : "bg-accent-amber"
                }`}
              />
              {linkStatus}
            </span>
            <span
              className={`hq-pill text-xs font-medium ${
                systemHealth === "healthy"
                  ? "text-accent-emerald"
                  : systemHealth === "degraded"
                    ? "text-accent-amber"
                    : "text-ink-tertiary"
              }`}
            >
              <span
                className={`h-2 w-2 rounded-full ${
                  systemHealth === "healthy"
                    ? "bg-accent-emerald"
                    : systemHealth === "degraded"
                      ? "bg-accent-amber"
                      : "bg-ink-tertiary"
                }`}
              />
              {systemHealth === "healthy" ? "API healthy" : systemHealth === "degraded" ? "API degraded" : "Checking…"}
            </span>
            <button type="button" className="hq-pill relative" aria-label="Notifications">
              <Bell className="h-4 w-4" />
              {notificationCount > 0 ? (
                <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-accent-amber text-[10px] font-bold text-white">
                  {notificationCount}
                </span>
              ) : null}
            </button>
            <button
              type="button"
              className="hq-pill text-xs"
              onClick={() => setThemeDark((d) => !d)}
              aria-pressed={themeDark}
            >
              {themeDark ? "Cockpit" : "Cream"}
            </button>
          </div>
        </div>
      </header>
    </>
  );
}
