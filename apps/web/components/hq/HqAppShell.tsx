"use client";

import type { ReactNode } from "react";

import { HqShellProvider } from "@/lib/hq/hq-shell-context";

import { HqContentHeader } from "./HqContentHeader";
import { HqSidebar } from "./HqSidebar";

export function HqAppShell({ children }: { children: ReactNode }) {
  return (
    <HqShellProvider>
      <div className="flex min-h-screen bg-cream-page">
        <HqSidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <HqContentHeader />
          <main className="flex-1 overflow-auto">{children}</main>
        </div>
      </div>
    </HqShellProvider>
  );
}
