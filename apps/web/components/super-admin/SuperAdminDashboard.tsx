"use client";

import { Building2, Cpu, DollarSign, TrendingUp } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { CreamCard } from "@/components/ui/CreamCard";
import { HealthDot } from "@/components/super-admin/HealthDot";
import { StatCard } from "@/components/super-admin/StatCard";
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

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!stats) return <p className="text-sm text-ink-secondary">Loading platform stats…</p>;

  const chartData = revenue?.growth_12m ?? [];
  const subTotal = stats.active_subscriptions + stats.trial_subscriptions;
  const activePct = subTotal > 0 ? Math.round((stats.active_subscriptions / subTotal) * 100) : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-ink-secondary">Platform-wide overview for operators with super_admin access.</p>
        <div className="flex flex-wrap gap-2 text-sm">
          <Link href="/super-admin/tenants" className="rounded-lg border border-cream-border px-3 py-1.5 hover:bg-cream-alt">
            Tenants
          </Link>
          <Link href="/super-admin/billing" className="rounded-lg border border-cream-border px-3 py-1.5 hover:bg-cream-alt">
            Billing
          </Link>
          <Link href="/super-admin/system" className="rounded-lg border border-cream-border px-3 py-1.5 hover:bg-cream-alt">
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
          iconClass="text-accent-cobalt"
          iconBgClass="bg-accent-cobalt-soft"
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
        <CreamCard className="p-5">
          <h3 className="text-sm font-semibold text-ink-primary">Subscriptions</h3>
          <p className="mt-1 text-xs text-ink-secondary">Active vs trial</p>
          <div className="mt-4 flex items-center justify-between text-sm">
            <span>Active {stats.active_subscriptions}</span>
            <span>Trial {stats.trial_subscriptions}</span>
          </div>
          <div className="mt-3 h-3 overflow-hidden rounded-full bg-cream-muted">
            <div className="h-full bg-accent-emerald" style={{ width: `${activePct}%` }} />
          </div>
        </CreamCard>

        <CreamCard className="p-5">
          <h3 className="text-sm font-semibold text-ink-primary">System health</h3>
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
                    <span className="text-ink-secondary">{label}</span>
                    <span className="flex items-center gap-2 font-medium capitalize text-ink-primary">
                      <HealthDot status={status} />
                      {status}
                    </span>
                  </li>
                ))}
              </>
            ) : (
              <li className="text-ink-secondary">Checking…</li>
            )}
          </ul>
        </CreamCard>
      </div>

      <CreamCard className="p-5">
        <h3 className="text-sm font-semibold text-ink-primary">Revenue growth (12 months)</h3>
        <div className="mt-4 h-64">
          {chartData.length === 0 ? (
            <p className="flex h-full items-center justify-center text-sm text-ink-secondary">No revenue data yet</p>
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
      </CreamCard>
    </div>
  );
}
