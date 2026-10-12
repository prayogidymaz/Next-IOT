import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "destructive";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  children: ReactNode;
};

const VARIANT: Record<ButtonVariant, string> = {
  primary:
    "bg-slate-900 text-white hover:bg-slate-800 shadow-sm active:scale-[0.98]",
  secondary:
    "border border-slate-200 bg-white text-slate-900 hover:bg-slate-50 shadow-sm active:scale-[0.98]",
  ghost: "text-slate-700 hover:bg-slate-100",
  destructive: "bg-red-600 text-white hover:bg-red-700",
};

export function Button(props: ButtonProps) {
  const { variant = "primary", className = "", children, ...rest } = props;
  const style = VARIANT[variant];
  return (
    <button
      type="button"
      className={`inline-flex items-center justify-center gap-2 rounded-md px-4 py-2.5 text-sm font-medium transition ${style} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
