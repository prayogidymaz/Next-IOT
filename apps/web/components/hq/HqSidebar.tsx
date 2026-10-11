"use client";

import { ChevronDown, ChevronLeft, ChevronRight, UserCircle2 } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { hqNavSectionsForRole, type HqNavSection } from "@/lib/hq/nav-config";
import { useHqShell } from "@/lib/hq/hq-shell-context";

function isActive(pathname: string, href: string) {
  if (href === "/dashboard") return pathname === "/dashboard";
  if (href === "/control-center") return pathname === "/control-center";
  if (href === "/device-profiles") return pathname.startsWith("/device-profiles");
  if (href === "/settings") return pathname === "/settings";
  return pathname === href || pathname.startsWith(`${href}/`);
}

function sectionOpenDefault(sections: HqNavSection[]): Record<string, boolean> {
  const out: Record<string, boolean> = {};
  for (const s of sections) out[s.id] = true;
  return out;
}

export function HqSidebar() {
  const pathname = usePathname();
  const { collapsed, toggleCollapsed, tenant, setTenant, tenants, userRole, alarmCount } = useHqShell();
  const sections = hqNavSectionsForRole(userRole);
  const [openSections, setOpenSections] = useState<Record<string, boolean>>(() => sectionOpenDefault(sections));

  useEffect(() => {
    const raw = localStorage.getItem("hq_nav_sections_open");
    if (raw) {
      try {
        const parsed = JSON.parse(raw) as Record<string, boolean>;
        setOpenSections((prev) => ({ ...prev, ...parsed }));
      } catch {
        /* ignore */
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("hq_nav_sections_open", JSON.stringify(openSections));
  }, [openSections]);

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

      <nav className="flex-1 space-y-3 overflow-y-auto p-3">
        {sections.map((section) => {
          const open = openSections[section.id] !== false;
          return (
            <div key={section.id}>
              {!collapsed && section.label ? (
                <button
                  type="button"
                  onClick={() =>
                    setOpenSections((prev) => ({
                      ...prev,
                      [section.id]: !open,
                    }))
                  }
                  className="mb-1 flex w-full items-center justify-between px-3 text-[10px] font-bold uppercase tracking-wider text-ink-tertiary"
                >
                  {section.label}
                  {section.collapsible ? <ChevronDown className={`h-3 w-3 transition ${open ? "" : "-rotate-90"}`} /> : null}
                </button>
              ) : null}
              {open || collapsed ? (
                <div className="space-y-1">
                  {section.items.map((item) => {
                    const active = isActive(pathname, item.href);
                    const Icon = item.icon;
                    const badge = item.badgeKey === "alarms" && alarmCount > 0 ? alarmCount : null;
                    return (
                      <Link
                        key={`${section.id}-${item.label}-${item.href}`}
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
                        {!collapsed ? (
                          <span className="flex min-w-0 flex-1 items-center justify-between gap-2 truncate">
                            <span className="truncate">{item.label}</span>
                            <span className="flex shrink-0 items-center gap-1">
                              {badge !== null ? (
                                <span className="rounded-full bg-red-100 px-1.5 text-[10px] font-bold text-red-700">{badge}</span>
                              ) : null}
                              {item.shortcut ? (
                                <span className="hidden font-mono text-[9px] text-ink-tertiary xl:inline">{item.shortcut}</span>
                              ) : null}
                            </span>
                          </span>
                        ) : null}
                      </Link>
                    );
                  })}
                </div>
              ) : null}
            </div>
          );
        })}
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
