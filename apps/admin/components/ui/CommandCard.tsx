import type { ReactNode } from "react";

type CommandCardProps = {
  children: ReactNode;
  className?: string;
  hover?: boolean;
};

export function CommandCard({ children, className = "", hover = false }: CommandCardProps) {
  return (
    <div className={`command-card ${hover ? "transition hover:border-command-accent/30" : ""} ${className}`}>
      {children}
    </div>
  );
}
