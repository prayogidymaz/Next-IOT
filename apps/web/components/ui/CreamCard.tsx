"use client";

import type { ReactNode } from "react";

type CreamCardProps = {
  children: ReactNode;
  className?: string;
  hover?: boolean;
};

export function CreamCard({ children, className = "", hover = false }: CreamCardProps) {
  return (
    <div className={`${hover ? "cream-card-hover" : "cream-card"} ${className}`}>{children}</div>
  );
}
