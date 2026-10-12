"use client";

import { Bell, ChevronRight, Moon, Search, Sun, UserCircle2 } from "lucide-react";
import type { RefObject } from "react";

import { useAdminTheme } from "@/components/AdminThemeProvider";

type AdminTopBarProps = {
  title: string;
  breadcrumb?: string;
  searchRef?: RefObject<HTMLInputElement | null>;
  onOpenCommandPalette?: () => void;
};

export function AdminTopBar({ title, breadcrumb = "Platform", searchRef, onOpenCommandPalette }: AdminTopBarProps) {
  const { dark, toggleDark } = useAdminTheme();

  return (
    <header className="z-10 shrink-0 border-b border-slate-200 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">
      <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-4">
        <div>
          <nav className="mb-1 flex items-center gap-1 text-xs text-slate-500" aria-label="Breadcrumb">
            <span>{breadcrumb}</span>
            <ChevronRight className="h-3 w-3" />
            <span className="text-slate-700 dark:text-slate-300">{title}</span>
          </nav>
          <h1 className="text-xl font-semibold tracking-tight text-slate-900 dark:text-white">{title}</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="hidden items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500 md:flex dark:border-slate-700 dark:bg-slate-900">
            <Search className="h-4 w-4" />
            <input
              ref={searchRef}
              className="w-40 bg-transparent text-sm outline-none"
              placeholder="Search tenants…"
              aria-label="Search"
            />
            <button type="button" className="flex items-center gap-1" onClick={onOpenCommandPalette}>
              <kbd className="rounded border border-slate-200 px-1 text-[10px] dark:border-slate-600">⌘K</kbd>
            </button>
          </div>
          <button type="button" className="relative rounded-md border border-slate-200 p-2 dark:border-slate-700" aria-label="Notifications">
            <Bell className="h-4 w-4 text-slate-600" />
            <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
          </button>
          <button
            type="button"
            onClick={toggleDark}
            className="rounded-md border border-slate-200 p-2 dark:border-slate-700"
            aria-label="Toggle theme"
          >
            {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
          <div className="flex items-center gap-2 rounded-md border border-slate-200 px-2 py-1.5 dark:border-slate-700">
            <UserCircle2 className="h-8 w-8 text-blue-800" />
            <div className="hidden text-left sm:block">
              <p className="text-xs font-medium text-slate-900 dark:text-white">Super Admin</p>
              <p className="text-[10px] font-semibold uppercase tracking-wide text-blue-800">SUPER ADMIN</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
