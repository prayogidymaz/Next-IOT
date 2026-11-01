"use client";

import { useEffect, useRef } from "react";

import { useHqToast } from "@/hooks/useHqToast";
import { useHqShell } from "@/lib/hq/hq-shell-context";
import { useTenantRealtime, type RealtimeConnectionState } from "@/hooks/useTenantRealtime";

export type HqSystemStatus = "healthy" | "degraded" | "offline";

export function resolveHqSystemStatus(
  connection: RealtimeConnectionState,
  systemHealth: "healthy" | "degraded" | "unknown",
): HqSystemStatus {
  if (connection === "offline") return "offline";
  if (connection === "degraded" || systemHealth === "degraded") return "degraded";
  return "healthy";
}

export function SystemStatusBadge() {
  const { systemHealth } = useHqShell();
  const { connection } = useTenantRealtime();
  const { showToast } = useHqToast();
  const prev = useRef<HqSystemStatus | null>(null);

  const status = resolveHqSystemStatus(connection, systemHealth);

  useEffect(() => {
    if (prev.current === null) {
      prev.current = status;
      return;
    }
    if (prev.current === status) return;
    if (status === "degraded") {
      showToast("System status: degraded — check API or realtime connection", "error");
    } else if (status === "offline") {
      showToast("You appear offline — some features may not update", "error");
    } else if (status === "healthy" && prev.current !== "healthy") {
      showToast("System status: healthy", "success");
    }
    prev.current = status;
  }, [status, showToast]);

  if (status === "healthy") return null;

  if (status === "offline") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full border border-red-200 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
        🔴 Offline
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-amber-200 bg-amber-50 px-2 py-1 text-xs font-medium text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200">
      ⚠️ Degraded
    </span>
  );
}

export function useHqSystemStatus(): HqSystemStatus {
  const { systemHealth } = useHqShell();
  const { connection } = useTenantRealtime();
  return resolveHqSystemStatus(connection, systemHealth);
}
