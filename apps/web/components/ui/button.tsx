import { type ButtonHTMLAttributes } from "react";

type ButtonVariant = "default" | "outline" | "ghost";
type ButtonSize = "default" | "sm";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

export function Button({
  variant = "default",
  size = "default",
  className = "",
  type = "button",
  ...props
}: ButtonProps) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl font-medium transition active:scale-[0.98] disabled:pointer-events-none disabled:opacity-50";
  const sizes: Record<ButtonSize, string> = {
    default: "px-4 py-2.5 text-sm",
    sm: "px-3 py-1.5 text-xs",
  };
  const variants: Record<ButtonVariant, string> = {
    default: "bg-ink-primary text-white hover:bg-black/90",
    outline: "border border-cream-border bg-white text-ink-primary shadow-sm hover:bg-cream-muted",
    ghost: "text-ink-secondary hover:bg-cream-muted hover:text-ink-primary",
  };
  return (
    <button type={type} className={`${base} ${sizes[size]} ${variants[variant]} ${className}`.trim()} {...props} />
  );
}
