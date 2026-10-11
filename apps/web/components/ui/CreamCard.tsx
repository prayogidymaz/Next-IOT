"use client";

import type { ReactNode } from "react";

type CreamCardProps = {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  title?: string;
};

export function CreamCard({ children, className = "", hover = false, title }: CreamCardProps) {
  return (
    <div className={`${hover ? "cream-card-hover" : "cream-card"} ${className}`}>
      {title ? <h2 className="mb-3 text-sm font-semibold text-ink-primary">{title}</h2> : null}
      {children}
    </div>
  );
}
