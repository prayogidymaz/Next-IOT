"use client";

import type { ReactNode } from "react";

import { cn } from "@/src/lib/cn";

type Props = {
  breadcrumbs?: ReactNode;
  title: string;
  subtitle?: string;
  action?: ReactNode;
  actions?: ReactNode;
  className?: string;
};

export function PageHeader({ breadcrumbs, title, subtitle, action, actions, className }: Props) {
  const headerAction = action ?? actions;
  return (
    <header className={cn("mb-6 flex flex-col gap-3 md:flex-row md:items-start md:justify-between", className)}>
      <div className="min-w-0 space-y-1">
        {breadcrumbs ? <div className="text-sm text-muted-foreground">{breadcrumbs}</div> : null}
        <h1 className="text-xl font-semibold text-foreground md:text-2xl">{title}</h1>
        {subtitle ? <p className="text-sm text-muted-foreground md:text-base">{subtitle}</p> : null}
      </div>
      {headerAction ? <div className="shrink-0">{headerAction}</div> : null}
    </header>
  );
}
