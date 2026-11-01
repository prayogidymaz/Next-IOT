import type { HTMLAttributes } from "react";

import { cn } from "@/src/lib/cn";

type BadgeVariant = "default" | "outline";

type Props = HTMLAttributes<HTMLSpanElement> & {
  variant?: BadgeVariant;
};

export function Badge({ className, variant = "default", ...props }: Props) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        variant === "outline" && "border border-border bg-card text-foreground",
        variant === "default" && "bg-muted text-foreground",
        className,
      )}
      {...props}
    />
  );
}
