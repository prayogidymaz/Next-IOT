"use client";

import type { ReactNode } from "react";

import { cn } from "@/src/lib/cn";

type Variant = "no-data" | "no-permission" | "error" | "loading";

type Props = {
  variant?: Variant;
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
};

const defaultIcon: Record<Variant, string> = {
  "no-data": "📭",
  "no-permission": "🔒",
  error: "⚠️",
  loading: "⏳",
};

export function EmptyState({ variant = "no-data", icon, title, description, action, className }: Props) {
  return (
    <div className={cn("flex flex-col items-center justify-center rounded-xl border border-border bg-card px-6 py-10 text-center", className)}>
      <div className="text-3xl" aria-hidden>
        {icon ?? defaultIcon[variant]}
      </div>
      <h3 className="mt-3 text-base font-semibold text-foreground">{title}</h3>
      {description ? <p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p> : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
