import { Card } from "@next-iot/ui";
import type { ReactNode } from "react";

type AdminCardProps = {
  children: ReactNode;
  className?: string;
  hover?: boolean;
};

export function AdminCard({ children, className = "", hover = false }: AdminCardProps) {
  return (
    <Card className={className} shadow="sm" hover={hover}>
      {children}
    </Card>
  );
}
