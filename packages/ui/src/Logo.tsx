import type { ReactNode } from "react";

type LogoVariant = "dark" | "light" | "icon";

type LogoProps = {
  variant?: LogoVariant;
  className?: string;
};

export function Logo({ variant = "dark", className = "" }: LogoProps) {
  const textClass =
    variant === "light" ? "text-white" : variant === "icon" ? "text-sky-600" : "text-slate-900";
  const mark = (
    <span
      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-sky-500 to-emerald-500 text-sm font-bold text-white ${className}`}
      aria-hidden
    >
      N
    </span>
  );
  if (variant === "icon") return mark;
  return (
    <span className={`inline-flex items-center gap-2 font-semibold tracking-tight ${textClass} ${className}`}>
      {mark}
      <span>Next-IoT</span>
    </span>
  );
}

export function LogoMark({ children }: { children?: ReactNode }) {
  return children ?? <Logo variant="icon" />;
}
