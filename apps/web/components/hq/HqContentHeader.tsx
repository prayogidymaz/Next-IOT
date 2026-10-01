"use client";

import { Bell, ChevronRight } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { HQ_DOMAINS, type HqDomainId } from "@/lib/hq/domains";
import { titleForPath } from "@/lib/hq/nav-config";
import { useHqShell } from "@/lib/hq/hq-shell-context";

export function HqContentHeader() {
  const pathname = usePathname();
  const { domainId, setDomainId, notificationCount, systemHealth } = useHqShell();
  const title = titleForPath(pathname);

  return (
    <header className="sticky top-0 z-10 border-b border-cream-border bg-cream-page/95 px-6 py-4 backdrop-blur-md">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <nav className="mb-1 flex items-center gap-1 text-xs text-ink-tertiary">
            <Link href="/dashboard" className="hover:text-ink-secondary">
              Web HQ
            </Link>
            <ChevronRight className="h-3 w-3" />
            <span className="text-ink-secondary">{title}</span>
          </nav>
          <h1 className="text-xl font-semibold tracking-tight text-ink-primary md:text-2xl">{title}</h1>
        </div>

        <div className="flex flex-wrap items-center gap-2">
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
            {systemHealth === "healthy" ? "System healthy" : systemHealth === "degraded" ? "Degraded" : "Checking…"}
          </span>
          <button type="button" className="hq-pill relative">
            <Bell className="h-4 w-4" />
            {notificationCount > 0 ? (
              <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-accent-amber text-[10px] font-bold text-white">
                {notificationCount}
              </span>
            ) : null}
          </button>
        </div>
      </div>
    </header>
  );
}
