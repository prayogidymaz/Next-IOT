"use client";

import { Logo } from "@next-iot/ui";
import { Activity, Building2, LayoutDashboard, LogOut, Receipt, Settings } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { AdminThemeProvider } from "@/components/AdminThemeProvider";
import { AdminTopBar } from "@/components/AdminTopBar";
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

function ShellInner({ children, title }: { children: ReactNode; title: string }) {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    clearSessionTokens();
    router.replace("/login");
  }

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
      <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900">
        <div className="border-b border-slate-200 p-5 dark:border-slate-800">
          <Logo />
          <p className="mt-2 text-xs text-slate-500">Platform console</p>
        </div>
        <nav className="flex-1 space-y-1 p-3" aria-label="Admin">
          {NAV.map((item) => {
            const Icon = item.icon;
            const active = isActive(pathname, item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`admin-nav-link ${active ? "admin-nav-link-active" : ""}`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="space-y-1 border-t border-slate-200 p-3 dark:border-slate-800">
          <button type="button" className="admin-nav-link w-full">
            <Settings className="h-4 w-4" />
            Settings
          </button>
          <button type="button" onClick={logout} className="admin-nav-link w-full">
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <AdminTopBar title={title} />
        <main className="mx-auto w-full max-w-content flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}

export function AdminShell({ children, title }: { children: ReactNode; title: string }) {
  return (
    <AdminThemeProvider>
      <ShellInner title={title}>{children}</ShellInner>
    </AdminThemeProvider>
  );
}
