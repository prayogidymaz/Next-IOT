"use client";

import { useEffect, useState } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import { fetchSuperAdminStats } from "@/lib/api/super-admin";

export function SuperAdminDashboard() {
  const [stats, setStats] = useState<{
    total_tenants: number;
    active_tenants: number;
    mrr_idr: number;
    total_devices: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void fetchSuperAdminStats()
      .then(setStats)
      .catch(() => setError("Requires super_admin role"));
  }, []);

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!stats) return <p className="text-sm text-ink-secondary">Loading…</p>;

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <CreamCard title="Tenants">
        <p className="text-2xl font-semibold">{stats.total_tenants}</p>
        <p className="text-xs text-ink-secondary">{stats.active_tenants} active</p>
      </CreamCard>
      <CreamCard title="MRR (IDR)">
        <p className="text-2xl font-semibold">{stats.mrr_idr.toLocaleString("id-ID")}</p>
      </CreamCard>
      <CreamCard title="Devices">
        <p className="text-2xl font-semibold">{stats.total_devices}</p>
      </CreamCard>
    </div>
  );
}
