"use client";

import { useEffect, useState } from "react";

import { CommandCard } from "@/components/ui/CommandCard";
import { HealthDot } from "@/components/console/HealthDot";
import { fetchSuperAdminSystemHealth } from "@/lib/api/super-admin";
import type { SystemHealth } from "@/lib/api/super-admin";

const SERVICES: Array<{ key: keyof SystemHealth; label: string }> = [
  { key: "api", label: "API" },
  { key: "database", label: "PostgreSQL" },
  { key: "redis", label: "Redis" },
  { key: "emqx", label: "EMQX" },
  { key: "mqtt_subscriber", label: "MQTT Subscriber" },
  { key: "mqtt_publisher", label: "MQTT Publisher" },
  { key: "scheduler", label: "Scheduler" },
];

export function SuperAdminSystemPanel() {
  const [health, setHealth] = useState<SystemHealth | null>(null);

  useEffect(() => {
    void fetchSuperAdminSystemHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {SERVICES.map(({ key, label }) => {
          const status = health ? String(health[key]) : "unknown";
          return (
            <CommandCard key={key} className="p-5">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-command-text">{label}</h3>
                <HealthDot status={status} />
              </div>
              <p className="mt-2 text-sm capitalize text-command-secondary">{status}</p>
            </CommandCard>
          );
        })}
      </div>

      <CommandCard className="grid gap-4 p-5 md:grid-cols-3">
        <div>
          <p className="text-xs uppercase text-command-tertiary">Last check</p>
          <p className="text-sm font-medium">{health ? new Date(health.checked_at).toLocaleString() : "—"}</p>
        </div>
        <div>
          <p className="text-xs uppercase text-command-tertiary">Platform uptime</p>
          <p className="text-sm font-medium">API process healthy</p>
        </div>
        <div>
          <p className="text-xs uppercase text-command-tertiary">Error rate</p>
          <p className="text-sm font-medium text-command-secondary">Not instrumented in MVP</p>
        </div>
      </CommandCard>
    </div>
  );
}
