type BadgeVariant = "default" | "success" | "warning" | "danger" | "info" | "neutral";

type BadgeProps = {
  children: string;
  variant?: BadgeVariant;
};

const STYLES: Record<BadgeVariant, string> = {
  default: "bg-slate-100 text-slate-800",
  success: "bg-emerald-50 text-emerald-800",
  warning: "bg-amber-50 text-amber-800",
  danger: "bg-red-50 text-red-800",
  info: "bg-sky-50 text-sky-800",
  neutral: "bg-slate-50 text-slate-600",
};

export function Badge({ children, variant = "default" }: BadgeProps) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${STYLES[variant]}`}>
      {children}
    </span>
  );
}
