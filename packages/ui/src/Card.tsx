import type { ReactNode } from "react";

type CardShadow = "sm" | "md" | "none";

type CardProps = {
  children: ReactNode;
  className?: string;
  shadow?: CardShadow;
  hover?: boolean;
};

const SHADOW: Record<CardShadow, string> = {
  none: "border border-slate-200",
  sm: "border border-slate-200 shadow-sm",
  md: "border border-slate-200 shadow-md",
};

export function Card({ children, className = "", shadow = "sm", hover = false }: CardProps) {
  return (
    <div
      className={`rounded-xl bg-white ${SHADOW[shadow]} ${hover ? "transition hover:shadow-md hover:-translate-y-0.5" : ""} ${className}`}
    >
      {children}
    </div>
  );
}
