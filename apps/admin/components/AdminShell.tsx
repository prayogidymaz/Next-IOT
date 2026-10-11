"use client";

import { Activity, Building2, LayoutDashboard, LogOut, Receipt } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { clearSessionTokens } from "@/lib/auth/session";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/tenants", label: "Tenants", icon: Building2 },
  { href: "/billing", label: "Billing", icon: Receipt },
  { href: "/system", label: "System", icon: Activity },
] as const;

function isActive(pathname: string, href: string) {
  if (href === "/dashboard") return pathname === "/dashboard";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function AdminShell({ children, title }: { children: ReactNode; title: string }) {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    clearSessionTokens();
    router.replace("/login");
  }

  return (
    <div className="flex min-h-screen bg-command-bg">
      <aside className="flex w-60 shrink-0 flex-col border-r border-command-border bg-command-panel">
        <div className="border-b border-command-border p-4">
          <p className="font-mono text-xs uppercase tracking-[0.2em] text-command-accent">Next-IoT</p>
          <p className="mt-1 text-sm font-semibold">Mission Control</p>
          <p className="text-xs text-command-tertiary">Super admin console</p>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {NAV.map((item) => {
            const Icon = item.icon;
            const active = isActive(pathname, item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`command-nav-link ${active ? "command-nav-link-active" : ""}`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <button
          type="button"
          onClick={logout}
          className="command-nav-link m-3 mt-auto border-command-border/60 text-command-secondary"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-command-border bg-command-panel/80 px-6 py-4 backdrop-blur">
          <p className="font-mono text-[10px] uppercase tracking-widest text-command-tertiary">Operator / Platform</p>
          <h1 className="mt-1 text-xl font-semibold tracking-tight">{title}</h1>
        </header>
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
