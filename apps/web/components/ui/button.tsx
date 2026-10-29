import { type ButtonHTMLAttributes } from "react";

type ButtonVariant = "default" | "outline";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
};

export function Button({ variant = "default", className = "", type = "button", ...props }: ButtonProps) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition active:scale-[0.98] disabled:pointer-events-none disabled:opacity-50";
  const variants: Record<ButtonVariant, string> = {
    default: "bg-ink-primary text-white hover:bg-black/90",
    outline: "border border-cream-border bg-white text-ink-primary shadow-sm hover:bg-cream-muted",
  };
  return <button type={type} className={`${base} ${variants[variant]} ${className}`.trim()} {...props} />;
}
