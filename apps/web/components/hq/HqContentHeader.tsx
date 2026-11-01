"use client";

import { Menu } from "lucide-react";
import { useEffect, useState } from "react";

import { CommandPalette } from "@/components/hq/CommandPalette";
import { HqBreadcrumb } from "@/components/hq/header/HqBreadcrumb";
import { NotificationBell } from "@/components/hq/header/NotificationBell";
import { QuickSearchTrigger } from "@/components/hq/header/QuickSearchTrigger";
import { SystemStatusBadge, useHqSystemStatus } from "@/components/hq/header/SystemStatusBadge";
import { UserMenu } from "@/components/hq/header/UserMenu";
import { LocaleSwitcher } from "@/components/hq/header/LocaleSwitcher";
import { SiteSwitcher } from "@/components/hq/header/SiteSwitcher";
import { ThemeToggle } from "@/src/components/ThemeToggle";

type Props = {
  onOpenMobileNav?: () => void;
};

export function HqContentHeader({ onOpenMobileNav }: Props) {
  const [paletteOpen, setPaletteOpen] = useState(false);
  const systemStatus = useHqSystemStatus();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <>
      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
      <header className="z-20 shrink-0 border-b border-border bg-background">
        <div className="flex items-center justify-between gap-3 px-4 py-3 md:px-6">
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <button
              type="button"
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border bg-card md:hidden"
              aria-label="Open navigation menu"
              onClick={onOpenMobileNav}
            >
              <Menu className="h-5 w-5" />
            </button>
            <HqBreadcrumb />
            <SiteSwitcher />
          </div>

          <div className="flex shrink-0 items-center gap-1">
            <SystemStatusBadge />
            <LocaleSwitcher />
            <QuickSearchTrigger onOpen={() => setPaletteOpen(true)} />
            <NotificationBell />
            <ThemeToggle />
            <UserMenu showHealthyDot={systemStatus === "healthy"} />
          </div>
        </div>
      </header>
    </>
  );
}
