"use client";

import { useEffect, useState } from "react";

import { AdminCard } from "@/components/ui/AdminCard";
import { getApiBaseUrl } from "@/lib/auth/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

export function AgriPlatformPanel() {
  const [stats, setStats] = useState<Record<string, unknown> | null>(null);
  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    void fetch(`${getApiBaseUrl()}/api/v1/super-admin/agriculture/stats`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then(setStats)
      .catch(() => setStats(null));
  }, []);
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <AdminCard className="p-4">
        <p className="text-sm text-slate-500">Total farms</p>
        <p className="text-2xl font-semibold">{String(stats?.total_farms ?? "—")}</p>
      </AdminCard>
      <AdminCard className="p-4">
        <p className="text-sm text-slate-500">Hectares</p>
        <p className="text-2xl font-semibold">{String(stats?.total_hectares ?? "—")}</p>
      </AdminCard>
      <AdminCard className="p-4">
        <p className="text-sm text-slate-500">Agri sensors</p>
        <p className="text-2xl font-semibold">{String(stats?.total_agri_sensors ?? "—")}</p>
      </AdminCard>
    </div>
  );
}
