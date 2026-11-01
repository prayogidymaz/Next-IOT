"use client";

import type { ReactNode } from "react";

type HqPageContentProps = {
  children: ReactNode;
  action?: ReactNode;
};

export function HqPageContent({ children, action }: HqPageContentProps) {
  return (
    <div className="container mx-auto max-w-7xl space-y-6 px-4 py-6 md:px-6 md:py-8 lg:px-8">
      {action ? <div className="flex justify-end">{action}</div> : null}
      {children}
    </div>
  );
}
