"use client";

import type { ReactNode } from "react";

type HqPageContentProps = {
  children: ReactNode;
  description?: string;
};

export function HqPageContent({ children, description }: HqPageContentProps) {
  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6 md:p-8">
      {description ? <p className="max-w-3xl text-sm text-ink-secondary">{description}</p> : null}
      {children}
    </div>
  );
}
