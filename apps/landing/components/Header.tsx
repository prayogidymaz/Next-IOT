"use client";

import { Logo } from "@next-iot/ui";
import Link from "next/link";
import { useState } from "react";

import { ThemeToggle } from "@/components/landing/ThemeToggle";
import { APP_URL } from "@/lib/site";

const NAV = [
  { href: "/features", label: "Features" },
  { href: "/pricing", label: "Pricing" },
  { href: "/about", label: "About" },
  { href: "/contact", label: "Contact" },
  { href: "/docs", label: "Docs" },
];

export function Header() {
  const [open, setOpen] = useState(false);
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/90">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 md:px-6">
        <Link href="/" className="shrink-0">
          <Logo />
        </Link>
        <nav className="hidden items-center gap-8 md:flex" aria-label="Main">
          {NAV.map((item) => (
            <Link key={item.href} href={item.href} className="text-sm text-slate-600 hover:text-slate-900">
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="hidden items-center gap-3 md:flex">
          <ThemeToggle />
          <Link href={`${APP_URL}/login`} className="text-sm font-medium text-slate-600 hover:text-slate-900 dark:text-slate-300">
            Login
          </Link>
          <Link
            href={`${APP_URL}/register`}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800"
          >
            Start Free Trial
          </Link>
        </div>
        <button
          type="button"
          className="rounded-md border border-slate-200 px-3 py-2 text-sm md:hidden"
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          Menu
        </button>
      </div>
      {open ? (
        <div className="border-t border-slate-200 px-4 py-4 md:hidden">
          <div className="flex flex-col gap-3">
            {NAV.map((item) => (
              <Link key={item.href} href={item.href} className="text-sm text-slate-700" onClick={() => setOpen(false)}>
                {item.label}
              </Link>
            ))}
            <Link href={`${APP_URL}/register`} className="text-sm font-medium text-sky-600">
              Start Free Trial
            </Link>
          </div>
        </div>
      ) : null}
    </header>
  );
}
