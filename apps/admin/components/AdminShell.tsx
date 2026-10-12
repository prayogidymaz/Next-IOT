"use client";

import { Logo } from "@next-iot/ui";
import { LogOut, Settings } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState, type ReactNode } from "react";

import { AdminCommandPalette } from "@/components/AdminCommandPalette";
import { AdminThemeProvider } from "@/components/AdminThemeProvider";
import { AdminTopBar } from "@/components/AdminTopBar";
import { ADMIN_NAV_GROUPS } from "@/lib/admin-nav";
import { clearSessionTokens } from "@/lib/auth/session";

function isActive(pathname: string, href: string) {
  if (href === "/dashboard") return pathname === "/dashboard";
  return pathname === href || pathname.startsWith(`${href}/`);
}

function ShellInner({ children, title }: { children: ReactNode; title: string }) {
  const pathname = usePathname();
  const router = useRouter();
  const [paletteOpen, setPaletteOpen] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

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
        <nav className="flex-1 space-y-4 overflow-y-auto p-3" aria-label="Admin">
          {ADMIN_NAV_GROUPS.map((group) => (
            <div key={group.id}>
              <p className="mb-1 px-2 text-[10px] font-semibold uppercase tracking-wide text-slate-400">{group.label}</p>
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(pathname, item.href);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`admin-nav-link ${active ? "admin-nav-link-active" : ""}`}
                    >
                      <Icon className="h-4 w-4 shrink-0" />
                      <span className="truncate">{item.label}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
        <div className="space-y-1 border-t border-slate-200 p-3 dark:border-slate-800">
          <Link href="/settings" className="admin-nav-link">
            <Settings className="h-4 w-4" />
            Settings
          </Link>
          <button type="button" onClick={logout} className="admin-nav-link w-full">
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <AdminTopBar
          title={title}
          searchRef={searchRef}
          onOpenCommandPalette={() => setPaletteOpen(true)}
        />
        <main className="mx-auto w-full max-w-content flex-1 overflow-auto p-6">{children}</main>
      </div>
      <AdminCommandPalette
        open={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        onFocusSearch={() => searchRef.current?.focus()}
      />
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
