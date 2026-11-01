"use client";

import type { ReactNode } from "react";
import { useState } from "react";

import { HqToastProvider } from "@/hooks/useHqToast";
import { HqUserProvider } from "@/hooks/useHqUser";
import { HqShellProvider } from "@/lib/hq/hq-shell-context";

import { HqContentHeader } from "./HqContentHeader";
import { HqSidebar } from "./HqSidebar";

export function HqAppShell({ children }: { children: ReactNode }) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <HqShellProvider>
      <HqUserProvider>
        <HqToastProvider>
          <div className="flex h-screen bg-background">
            {mobileNavOpen ? (
              <button
                type="button"
                className="fixed inset-0 z-20 bg-black/40 md:hidden"
                aria-label="Close navigation overlay"
                onClick={() => setMobileNavOpen(false)}
              />
            ) : null}
            <HqSidebar mobileOpen={mobileNavOpen} onNavigate={() => setMobileNavOpen(false)} />
            <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
              <HqContentHeader onOpenMobileNav={() => setMobileNavOpen(true)} />
              <main className="flex-1 overflow-y-auto">{children}</main>
            </div>
          </div>
        </HqToastProvider>
      </HqUserProvider>
    </HqShellProvider>
  );
}
