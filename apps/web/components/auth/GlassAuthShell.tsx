"use client";

import Link from "next/link";
import type { ReactNode } from "react";

type GlassAuthShellProps = {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer?: ReactNode;
};

export function GlassAuthShell({ title, subtitle, children, footer }: GlassAuthShellProps) {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-cream-page px-4 py-12">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_50%_-10%,rgba(16,185,129,0.12),transparent)]" />
      <div className="relative w-full max-w-md cream-card p-8 shadow-card-md">
        <Link href="/" className="mb-8 inline-flex items-center gap-2 text-sm text-ink-secondary hover:text-ink-primary">
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-accent-emerald-soft text-xs font-bold text-accent-emerald">
            N
          </span>
          Next-IoT
        </Link>
        <h1 className="text-2xl font-semibold tracking-tight text-ink-primary">{title}</h1>
        <p className="mt-2 text-sm text-ink-secondary">{subtitle}</p>
        <div className="mt-8">{children}</div>
        {footer ? <div className="mt-6 text-center text-sm text-ink-secondary">{footer}</div> : null}
      </div>
    </div>
  );
}
