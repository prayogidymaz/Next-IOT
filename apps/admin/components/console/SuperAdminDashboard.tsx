"use client";

import { Building2, Cpu, DollarSign, TrendingUp } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { CommandCard } from "@/components/ui/CommandCard";
import { HealthDot } from "@/components/console/HealthDot";
import { StatCard } from "@/components/console/StatCard";
import {
  fetchSuperAdminRevenue,
  fetchSuperAdminStats,
  fetchSuperAdminSystemHealth,
  formatIdr,
} from "@/lib/api/super-admin";
import type { PlatformStats, RevenueReport, SystemHealth } from "@/lib/api/super-admin";

export function SuperAdminDashboard() {
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [revenue, setRevenue] = useState<RevenueReport | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([fetchSuperAdminStats(), fetchSuperAdminRevenue(12), fetchSuperAdminSystemHealth()])
      .then(([s, r, h]) => {
        setStats(s);
        setRevenue(r);
        setHealth(h);
      })
      .catch(() => setError("Requires super_admin role or API unavailable"));
  }, []);

  if (error) return <p className="text-sm text-red-400">{error}</p>;
  if (!stats) return <p className="text-sm text-command-secondary">Loading platform stats…</p>;

  const chartData = revenue?.growth_12m ?? [];
  const subTotal = stats.active_subscriptions + stats.trial_subscriptions;
  const activePct = subTotal > 0 ? Math.round((stats.active_subscriptions / subTotal) * 100) : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-command-secondary">Platform-wide overview for operators with super_admin access.</p>
        <div className="flex flex-wrap gap-2 text-sm">
          <Link href="/tenants" className="rounded-lg border border-command-border px-3 py-1.5 hover:bg-command-muted">
            Tenants
          </Link>
          <Link href="/billing" className="rounded-lg border border-command-border px-3 py-1.5 hover:bg-command-muted">
            Billing
          </Link>
          <Link href="/system" className="rounded-lg border border-command-border px-3 py-1.5 hover:bg-command-muted">
            System
          </Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Total Tenants"
          value={String(stats.total_tenants)}
          subtitle={`${stats.active_tenants} active`}
          icon={Building2}
          iconClass="text-command-accent"
          iconBgClass="bg-command-accent-soft"
        />
        <StatCard
          title="Devices Platform"
          value={String(stats.total_devices)}
          subtitle="Registered on platform"
          icon={Cpu}
          iconClass="text-accent-violet"
          iconBgClass="bg-accent-violet-soft"
        />
        <StatCard
          title="MRR (Rp)"
          value={formatIdr(stats.mrr_idr)}
          subtitle="Monthly recurring"
          icon={TrendingUp}
          iconClass="text-accent-emerald"
          iconBgClass="bg-accent-emerald-soft"
        />
        <StatCard
          title="Revenue MTD (Rp)"
          value={formatIdr(stats.revenue_mtd_idr)}
          subtitle="Month-to-date"
          icon={DollarSign}
          iconClass="text-accent-amber"
          iconBgClass="bg-accent-amber-soft"
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <CommandCard className="p-5">
          <h3 className="text-sm font-semibold text-command-text">Subscriptions</h3>
          <p className="mt-1 text-xs text-command-secondary">Active vs trial</p>
          <div className="mt-4 flex items-center justify-between text-sm">
            <span>Active {stats.active_subscriptions}</span>
            <span>Trial {stats.trial_subscriptions}</span>
          </div>
          <div className="mt-3 h-3 overflow-hidden rounded-full bg-cream-muted">
            <div className="h-full bg-accent-emerald" style={{ width: `${activePct}%` }} />
          </div>
        </CommandCard>

        <CommandCard className="p-5">
          <h3 className="text-sm font-semibold text-command-text">System health</h3>
          <ul className="mt-4 space-y-2 text-sm">
            {health ? (
              <>
                {(
                  [
                    ["API", health.api],
                    ["PostgreSQL", health.database],
                    ["Redis", health.redis],
                    ["EMQX", health.emqx],
                  ] as const
                ).map(([label, status]) => (
                  <li key={label} className="flex items-center justify-between gap-2">
                    <span className="text-command-secondary">{label}</span>
                    <span className="flex items-center gap-2 font-medium capitalize text-command-text">
                      <HealthDot status={status} />
                      {status}
                    </span>
                  </li>
                ))}
              </>
            ) : (
              <li className="text-command-secondary">Checking…</li>
            )}
          </ul>
        </CommandCard>
      </div>

      <CommandCard className="p-5">
        <h3 className="text-sm font-semibold text-command-text">Revenue growth (12 months)</h3>
        <div className="mt-4 h-64">
          {chartData.length === 0 ? (
            <p className="flex h-full items-center justify-center text-sm text-command-secondary">No revenue data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--cream-border, #e8e4dc)" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => formatIdr(Number(v))} />
                <Bar dataKey="revenue_idr" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </CommandCard>
    </div>
  );
}
