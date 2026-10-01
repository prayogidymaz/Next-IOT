"use client";

import { ChevronLeft, ChevronRight, UserCircle2 } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { HQ_NAV_SECTIONS } from "@/lib/hq/nav-config";
import { useHqShell } from "@/lib/hq/hq-shell-context";

function isActive(pathname: string, href: string) {
  if (href === "/dashboard") return pathname === "/dashboard";
  if (href === "/control-center") return pathname === "/control-center";
  if (href === "/settings") return pathname === "/settings";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function HqSidebar() {
  const pathname = usePathname();
  const { collapsed, toggleCollapsed, tenant, setTenant, tenants } = useHqShell();

  return (
    <aside
      className={`flex shrink-0 flex-col border-r border-cream-border bg-white transition-[width] duration-200 ${
        collapsed ? "w-[76px]" : "w-64"
      }`}
    >
      <div className="border-b border-cream-border p-4">
        <Link href="/dashboard" prefetch className="flex items-center gap-3">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-accent-emerald-soft text-sm font-bold text-accent-emerald">
            N
          </span>
          {!collapsed ? (
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-ink-primary">Next-IoT</p>
              <p className="truncate text-xs text-ink-secondary">Enterprise HQ</p>
            </div>
          ) : null}
        </Link>
        {!collapsed ? (
          <label className="mt-4 block text-xs text-ink-secondary">
            Tenant
            <select
              value={tenant}
              onChange={(e) => setTenant(e.target.value)}
              className="mt-1 w-full rounded-xl border border-cream-border bg-cream-alt px-2 py-2 text-sm font-medium text-ink-primary outline-none"
            >
              {tenants.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
        ) : null}
      </div>

      <nav className="flex-1 space-y-4 overflow-y-auto p-3">
        {HQ_NAV_SECTIONS.map((section) => (
          <div key={section.label ?? section.items[0]?.href}>
            {!collapsed && section.label ? (
              <p className="mb-2 px-3 text-[10px] font-bold uppercase tracking-wider text-ink-tertiary">
                {section.label}
              </p>
            ) : null}
            <div className="space-y-1">
              {section.items.map((item) => {
                const active = isActive(pathname, item.href);
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    prefetch
                    title={item.label}
                    className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
                      active
                        ? "bg-cream-muted font-semibold text-ink-primary shadow-sm"
                        : "text-ink-secondary hover:bg-cream-alt hover:text-ink-primary"
                    }`}
                  >
                    <span className={`rounded-lg p-1.5 ${active ? item.iconBgClass : "bg-cream-muted"}`}>
                      <Icon className={`h-4 w-4 ${active ? item.accentClass : "text-ink-tertiary"}`} />
                    </span>
                    {!collapsed ? <span className="truncate">{item.label}</span> : null}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-cream-border p-3">
        <div className={`mb-2 flex items-center gap-2 ${collapsed ? "justify-center" : ""}`}>
          <UserCircle2 className="h-8 w-8 shrink-0 text-accent-cobalt" />
          {!collapsed ? (
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-ink-primary">Operator</p>
              <p className="truncate text-xs text-ink-secondary">admin@nextiot.com</p>
            </div>
          ) : null}
        </div>
        <button
          type="button"
          onClick={toggleCollapsed}
          className="flex w-full items-center justify-center gap-2 rounded-xl border border-cream-border bg-cream-alt py-2 text-xs font-medium text-ink-secondary transition hover:bg-cream-muted"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          {!collapsed ? <span>Collapse sidebar</span> : null}
        </button>
      </div>
    </aside>
  );
}
