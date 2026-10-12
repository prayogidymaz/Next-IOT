"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { slug: "", label: "Overview" },
  { slug: "irrigation", label: "Irrigation" },
  { slug: "alerts", label: "Alerts" },
  { slug: "calendar", label: "Calendar" },
  { slug: "yield", label: "Yield" },
  { slug: "analytics", label: "Analytics" },
  { slug: "settings", label: "Settings" },
] as const;

export function AgriFarmLayout({ farmId, title, children }: { farmId: string; title: string; children: React.ReactNode }) {
  const pathname = usePathname();
  const base = `/agriculture/farms/${farmId}`;
  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <nav className="text-xs text-ink-tertiary">
            <Link href="/agriculture" className="text-emerald-600 hover:underline">Agriculture</Link>
            <span> / </span>
            <span>{title}</span>
          </nav>
          <h1 className="text-xl font-semibold text-ink-primary">{title}</h1>
        </div>
      </div>
      <div className="sticky top-0 z-10 flex flex-wrap gap-2 border-b border-border-subtle bg-surface pb-2">
        {TABS.map((tab) => {
          const href = tab.slug ? `${base}/${tab.slug}` : base;
          const active = pathname === href || (tab.slug === "" && pathname === base);
          return (
            <Link
              key={tab.slug}
              href={href}
              className={`rounded-full px-3 py-1 text-sm ${active ? "bg-emerald-600 text-white" : "bg-slate-100 text-ink-secondary"}`}
            >
              {tab.label}
            </Link>
          );
        })}
      </div>
      {children}
    </div>
  );
}
