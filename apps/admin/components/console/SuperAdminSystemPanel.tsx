"use client";

import { useEffect, useState } from "react";

import { AdminCard } from "@/components/ui/AdminCard";
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
            <AdminCard key={key} className="p-5">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-slate-900">{label}</h3>
                <HealthDot status={status} />
              </div>
              <p className="mt-2 text-sm capitalize text-slate-500">{status}</p>
            </AdminCard>
          );
        })}
      </div>

      <AdminCard className="grid gap-4 p-5 md:grid-cols-3">
        <div>
          <p className="text-xs uppercase text-slate-400">Last check</p>
          <p className="text-sm font-medium">{health ? new Date(health.checked_at).toLocaleString() : "—"}</p>
        </div>
        <div>
          <p className="text-xs uppercase text-slate-400">Platform uptime</p>
          <p className="text-sm font-medium">API process healthy</p>
        </div>
        <div>
          <p className="text-xs uppercase text-slate-400">Error rate</p>
          <p className="text-sm font-medium text-slate-500">Not instrumented in MVP</p>
        </div>
      </AdminCard>
    </div>
  );
}
