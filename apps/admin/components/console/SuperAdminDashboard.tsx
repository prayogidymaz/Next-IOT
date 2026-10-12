"use client";

import { Building2, Cpu, DollarSign, MessageSquare, TrendingUp, Users } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { AdminCard } from "@/components/ui/AdminCard";
import { WatchListSection } from "@/components/console/SuperAdminExtendedPanels";
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

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!stats) return <p className="text-sm text-slate-500">Loading platform stats…</p>;

  const chartData = revenue?.growth_12m ?? [];
  const subTotal = stats.active_subscriptions + stats.trial_subscriptions;
  const activePct = subTotal > 0 ? Math.round((stats.active_subscriptions / subTotal) * 100) : 0;

  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-500">Platform-wide overview for super_admin operators.</p>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatCard title="Total tenants" value={String(stats.total_tenants)} subtitle={`${stats.active_tenants} active`} icon={Building2} />
        <StatCard title="Active subs" value={String(stats.active_subscriptions)} subtitle={`${stats.trial_subscriptions} trial`} icon={Users} />
        <StatCard title="MRR" value={formatIdr(stats.mrr_idr)} subtitle="Monthly recurring" icon={TrendingUp} />
        <StatCard title="ARR" value={formatIdr(stats.arr_idr ?? stats.mrr_idr * 12)} subtitle="Annual run rate" icon={DollarSign} />
        <StatCard title="Devices" value={String(stats.total_devices)} subtitle="Platform-wide" icon={Cpu} />
        <StatCard title="Messages today" value={String(stats.messages_today ?? 0)} subtitle="Telemetry + MQTT" icon={MessageSquare} />
      </div>

      <WatchListSection />

      <div className="flex flex-wrap gap-2">
        <Link href="/announcements" className="rounded-md bg-blue-800 px-4 py-2 text-sm font-medium text-white hover:bg-blue-900">
          Send announcement
        </Link>
        <Link href="/system-logs" className="rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50">
          View logs
        </Link>
        <Link href="/billing" className="rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50">
          Trigger billing
        </Link>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <AdminCard className="p-5">
          <h3 className="text-sm font-semibold text-slate-900">Subscriptions</h3>
          <p className="mt-1 text-xs text-slate-500">Active vs trial</p>
          <div className="mt-4 flex items-center justify-between text-sm">
            <span>Active {stats.active_subscriptions}</span>
            <span>Trial {stats.trial_subscriptions}</span>
          </div>
          <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-100">
            <div className="h-full bg-emerald-500" style={{ width: `${activePct}%` }} />
          </div>
        </AdminCard>

        <AdminCard className="p-5">
          <h3 className="text-sm font-semibold text-slate-900">System health</h3>
          <ul className="mt-4 space-y-2 text-sm">
            {health ? (
              (
                [
                  ["API", health.api],
                  ["PostgreSQL", health.database],
                  ["Redis", health.redis],
                  ["EMQX", health.emqx],
                ] as const
              ).map(([label, status]) => (
                <li key={label} className="flex items-center justify-between gap-2">
                  <span className="text-slate-500">{label}</span>
                  <span className="flex items-center gap-2 font-medium capitalize text-slate-900">
                    <HealthDot status={status} />
                    {status}
                  </span>
                </li>
              ))
            ) : (
              <li className="text-slate-500">Checking…</li>
            )}
          </ul>
        </AdminCard>
      </div>

      <AdminCard className="p-5">
        <h3 className="text-sm font-semibold text-slate-900">Revenue growth (12 months)</h3>
        <div className="mt-4 h-72">
          {chartData.length === 0 ? (
            <p className="flex h-full items-center justify-center text-sm text-slate-500">No revenue data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => formatIdr(Number(v))} />
                <Bar dataKey="revenue_idr" fill="#1e40af" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </AdminCard>
    </div>
  );
}
