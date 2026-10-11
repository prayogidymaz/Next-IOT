"use client";

import { Activity, AlertTriangle, Database, Radio, Wifi } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { AnimatedStat } from "@/components/dashboard/AnimatedStat";
import { AlarmSeverityBadge } from "@/components/dashboard/AlarmSeverityBadge";
import { DeviceStatusHeatmap } from "@/components/dashboard/DeviceStatusHeatmap";
import { CreamCard } from "@/components/ui/CreamCard";
import { useTenantRealtime } from "@/hooks/useTenantRealtime";
import { acknowledgeAlarm, listAlarms, type AlarmItem } from "@/lib/api/alarms";
import { listDevices } from "@/lib/api/devices";
import type { DeviceResponse } from "@/lib/api/devices-schemas";
import { HqPageContent } from "@/components/hq/HqPageContent";
import { useHqShell } from "@/lib/hq/hq-shell-context";

function devicesOnline(devices: DeviceResponse[]): number {
  return devices.filter((d) => d.status === "online").length;
}

function severityBreakdown(alarms: AlarmItem[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const a of alarms) {
    out[a.severity] = (out[a.severity] ?? 0) + 1;
  }
  return out;
}

export function TenantPowerDashboard() {
  const { tenant } = useHqShell();
  const { connection, messagesPerMin } = useTenantRealtime();
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [alarms, setAlarms] = useState<AlarmItem[]>([]);
  const [streamRows, setStreamRows] = useState<{ t: string; v: number }[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([listDevices(), listAlarms({ status: "active" })])
      .then(([d, a]) => {
        setDevices(d);
        setAlarms(a);
      })
      .catch(() => setError("Failed to load fleet metrics"));
  }, []);

  useEffect(() => {
    const id = window.setInterval(() => {
      setStreamRows((prev) => {
        const next = [...prev, { t: new Date().toLocaleTimeString(), v: Math.round(Math.random() * 40 + messagesPerMin) }];
        return next.slice(-24);
      });
    }, 4000);
    return () => window.clearInterval(id);
  }, [messagesPerMin]);

  const online = useMemo(() => devicesOnline(devices), [devices]);
  const activeAlarms = alarms.filter((a) => a.status === "active");
  const sev = useMemo(() => severityBreakdown(activeAlarms), [activeAlarms]);
  const dataVolumeGb = useMemo(() => ((devices.length * 1.2 + messagesPerMin * 0.02) / 1024).toFixed(2), [devices.length, messagesPerMin]);

  async function ack(id: string) {
    await acknowledgeAlarm(id);
    setAlarms((prev) => prev.filter((a) => a.id !== id));
  }

  return (
    <HqPageContent description={`Fleet command · ${tenant}`}>
      {error ? <p className="mb-4 text-sm text-red-600">{error}</p> : null}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <CreamCard hover className="p-5">
          <div className="flex items-center justify-between">
            <Radio className="h-5 w-5 text-accent-emerald" />
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold uppercase text-accent-emerald">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent-emerald" />
              Live
            </span>
          </div>
          <p className="mt-3 text-sm text-ink-secondary">Devices online</p>
          <p className="mt-1 text-2xl font-semibold">
            <AnimatedStat value={online} />
            <span className="text-base font-normal text-ink-tertiary"> / {devices.length}</span>
          </p>
          <p className="mt-1 text-xs text-ink-tertiary">+2 vs 24h avg (est.)</p>
        </CreamCard>

        <CreamCard hover className="p-5">
          <Activity className="h-5 w-5 text-accent-cobalt" />
          <p className="mt-3 text-sm text-ink-secondary">Messages / min</p>
          <p className="mt-1 text-2xl font-semibold">
            <AnimatedStat value={messagesPerMin} />
          </p>
          <p className="mt-1 text-xs text-ink-tertiary">
            SSE {connection === "connected" ? "connected" : connection}
          </p>
        </CreamCard>

        <CreamCard hover className="p-5">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          <p className="mt-3 text-sm text-ink-secondary">Active alarms</p>
          <p className="mt-1 text-2xl font-semibold">
            <AnimatedStat value={activeAlarms.length} />
          </p>
          <p className="mt-1 text-xs text-ink-tertiary">
            {Object.entries(sev)
              .map(([k, v]) => `${k}:${v}`)
              .join(" · ") || "All clear"}
          </p>
        </CreamCard>

        <CreamCard hover className="p-5">
          <Database className="h-5 w-5 text-accent-violet" />
          <p className="mt-3 text-sm text-ink-secondary">Data volume today</p>
          <p className="mt-1 text-2xl font-semibold font-mono">{dataVolumeGb} GB</p>
          <p className="mt-1 text-xs text-ink-tertiary">+8% vs yesterday (est.)</p>
        </CreamCard>
      </section>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <CreamCard className="p-4">
          <h2 className="text-sm font-semibold text-ink-primary">Live telemetry (5 min window)</h2>
          <div className="mt-3 h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={streamRows}>
                <XAxis dataKey="t" hide />
                <YAxis hide />
                <Tooltip />
                <Area type="monotone" dataKey="v" stroke="#2563EB" fill="#DBEAFE" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CreamCard>
        <CreamCard className="p-4">
          <h2 className="text-sm font-semibold text-ink-primary">Device status heatmap</h2>
          <DeviceStatusHeatmap devices={devices} />
        </CreamCard>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <CreamCard className="p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Recent alarms</h2>
            <Link href="/alarms" className="text-xs text-accent-cobalt hover:underline">
              View all
            </Link>
          </div>
          <ul className="mt-3 space-y-2">
            {activeAlarms.slice(0, 5).map((a) => (
              <li key={a.id} className="flex items-start justify-between gap-2 rounded-lg border border-cream-border px-2 py-2 text-sm">
                <div>
                  <AlarmSeverityBadge severity={a.severity} />
                  <p className="mt-1 font-medium">{a.title}</p>
                </div>
                <button type="button" className="hq-btn-soft shrink-0 px-2 py-1 text-xs" onClick={() => void ack(a.id)}>
                  Ack
                </button>
              </li>
            ))}
            {activeAlarms.length === 0 ? <p className="text-sm text-ink-secondary">No active alarms</p> : null}
          </ul>
        </CreamCard>

        <CreamCard className="p-4">
          <h2 className="text-sm font-semibold">Rule activity</h2>
          <ul className="mt-3 space-y-2 text-sm text-ink-secondary">
            <li className="rounded-lg border border-cream-border px-2 py-2">Humidity threshold → notify email (2m ago)</li>
            <li className="rounded-lg border border-cream-border px-2 py-2">Offline detector → create alarm (14m ago)</li>
            <li className="rounded-lg border border-cream-border px-2 py-2">OTA rollout guard → pause mission (1h ago)</li>
          </ul>
          <Link href="/studio/automation" className="mt-3 inline-block text-xs text-accent-cobalt hover:underline">
            Open automations
          </Link>
        </CreamCard>

        <CreamCard className="p-4">
          <h2 className="text-sm font-semibold">System metrics</h2>
          <div className="mt-4 space-y-3 font-mono text-xs">
            {[
              { label: "Ingest CPU", pct: 42 },
              { label: "Rule engine", pct: 28 },
              { label: "Storage", pct: 61 },
            ].map((g) => (
              <div key={g.label}>
                <div className="mb-1 flex justify-between text-ink-secondary">
                  <span>{g.label}</span>
                  <span>{g.pct}%</span>
                </div>
                <div className="h-2 rounded-full bg-cream-muted">
                  <div className="h-2 rounded-full bg-accent-cobalt" style={{ width: `${g.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </CreamCard>
      </div>

      <CreamCard className="mt-6 p-4">
        <div className="flex items-center gap-2">
          <Wifi className="h-4 w-4 text-accent-indigo" />
          <h2 className="text-sm font-semibold">Fleet map</h2>
        </div>
        <p className="mt-2 text-sm text-ink-secondary">
          Mapbox/Leaflet integration — device markers from geolocation attributes (placeholder grid).
        </p>
        <div className="mt-3 grid h-40 grid-cols-6 gap-1 rounded-xl border border-cream-border bg-cream-alt p-2">
          {devices.slice(0, 18).map((d) => (
            <Link
              key={d.id}
              href={`/devices/${d.id}`}
              title={d.name}
              className={`rounded-md border text-[10px] font-mono leading-tight ${
                d.status === "online"
                  ? "border-accent-emerald/40 bg-accent-emerald-soft text-accent-emerald"
                  : d.status === "offline"
                    ? "border-red-200 bg-red-50 text-red-700"
                    : "border-accent-amber/40 bg-accent-amber-soft text-accent-amber"
              } flex items-center justify-center p-1`}
            >
              {d.name.slice(0, 6)}
            </Link>
          ))}
        </div>
      </CreamCard>
    </HqPageContent>
  );
}
