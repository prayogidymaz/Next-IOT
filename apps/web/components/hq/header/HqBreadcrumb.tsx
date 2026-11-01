"use client";

import { ChevronRight } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { titleForPath } from "@/lib/hq/nav-config";

export function HqBreadcrumb() {
  const pathname = usePathname();
  const title = titleForPath(pathname);

  return (
    <nav className="flex min-w-0 items-center gap-1 text-xs text-muted-foreground md:text-sm" aria-label="Breadcrumb">
      <Link href="/dashboard" className="shrink-0 hover:text-foreground">
        Web HQ
      </Link>
      <ChevronRight className="hidden h-3.5 w-3.5 shrink-0 sm:inline" aria-hidden />
      <span className="hidden truncate text-foreground sm:inline">{title}</span>
      <span className="truncate text-foreground sm:hidden">{title.split(" ")[0]}</span>
    </nav>
  );
}
