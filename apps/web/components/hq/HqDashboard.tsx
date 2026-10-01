"use client";

import {
  Activity,
  Cpu,
  MapPin,
  Radio,
  RefreshCw,
  Shield,
  Sprout,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { useMemo } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import { getDomain } from "@/lib/hq/domains";
import { useHqShell } from "@/lib/hq/hq-shell-context";

import { HqPageContent } from "./HqPageContent";

const METRICS_BY_DOMAIN = {
  "smart-home": [
    { label: "Active rooms", value: "24", delta: "+2 today", icon: Zap, soft: "bg-accent-emerald-soft", iconColor: "text-accent-emerald" },
    { label: "Energy today", value: "18.4 kWh", delta: "-6% vs avg", icon: Activity, soft: "bg-accent-cobalt-soft", iconColor: "text-accent-cobalt" },
    { label: "Automations", value: "12 running", delta: "All healthy", icon: Cpu, soft: "bg-accent-violet-soft", iconColor: "text-accent-violet" },
    { label: "Uptime", value: "99.98%", delta: "Live", icon: Shield, soft: "bg-accent-emerald-soft", iconColor: "text-accent-emerald" },
  ],
  "smart-farming": [
    { label: "Field nodes online", value: "86", delta: "Live", icon: Sprout, soft: "bg-accent-emerald-soft", iconColor: "text-accent-emerald" },
    { label: "Soil moisture avg", value: "42%", delta: "Optimal band", icon: Activity, soft: "bg-accent-cobalt-soft", iconColor: "text-accent-cobalt" },
    { label: "Irrigation zones", value: "7 active", delta: "2 scheduled", icon: MapPin, soft: "bg-accent-amber-soft", iconColor: "text-accent-amber" },
    { label: "Crop alerts", value: "1 warning", delta: "Review", icon: Shield, soft: "bg-accent-amber-soft", iconColor: "text-accent-amber" },
  ],
  cyberdeck: [
    { label: "Mesh nodes", value: "14", delta: "RSSI stable", icon: Radio, soft: "bg-accent-indigo-soft", iconColor: "text-accent-indigo" },
    { label: "PTT channels", value: "3 open", delta: "Codec2 1200", icon: Activity, soft: "bg-accent-cobalt-soft", iconColor: "text-accent-cobalt" },
    { label: "Bridge status", value: "Connected", delta: "Orange Pi", icon: Cpu, soft: "bg-accent-indigo-soft", iconColor: "text-accent-indigo" },
    { label: "Ops uptime", value: "100%", delta: "24h window", icon: Shield, soft: "bg-accent-emerald-soft", iconColor: "text-accent-emerald" },
  ],
  drone: [
    { label: "Fleet airborne", value: "6 / 18", delta: "2 missions", icon: MapPin, soft: "bg-accent-amber-soft", iconColor: "text-accent-amber" },
    { label: "Delivery SLA", value: "94%", delta: "+1.2%", icon: Activity, soft: "bg-accent-emerald-soft", iconColor: "text-accent-emerald" },
    { label: "Geofence breaches", value: "0", delta: "Clear", icon: Shield, soft: "bg-accent-cobalt-soft", iconColor: "text-accent-cobalt" },
    { label: "Battery avg", value: "71%", delta: "Swap 2 units", icon: Zap, soft: "bg-accent-amber-soft", iconColor: "text-accent-amber" },
  ],
  robotics: [
    { label: "AMR online", value: "22", delta: "3 charging", icon: Cpu, soft: "bg-accent-violet-soft", iconColor: "text-accent-violet" },
    { label: "Line OEE", value: "87.2%", delta: "+0.4%", icon: Activity, soft: "bg-accent-emerald-soft", iconColor: "text-accent-emerald" },
    { label: "Safety interlocks", value: "OK", delta: "0 faults", icon: Shield, soft: "bg-accent-cobalt-soft", iconColor: "text-accent-cobalt" },
    { label: "Mission queue", value: "5", delta: "2 urgent", icon: MapPin, soft: "bg-accent-violet-soft", iconColor: "text-accent-violet" },
  ],
} as const;

const ACTIVITY = [
  { time: "12:04:18", level: "info", message: "Telemetry ingest P95 118ms — within SLO" },
  { time: "12:03:52", level: "success", message: "Device batch heartbeat — 248 nodes acknowledged" },
  { time: "12:02:11", level: "warn", message: "Alert rule triggered: humidity threshold Field B-2" },
  { time: "12:01:03", level: "info", message: "Webhook delivery 200 OK — partner.integration.acme" },
  { time: "11:58:44", level: "info", message: "OTA rollout 78% complete — firmware v2.4.1" },
];

export function HqDashboard() {
  const { domainId, tenant } = useHqShell();
  const domain = getDomain(domainId);
  const metrics = useMemo(() => METRICS_BY_DOMAIN[domainId], [domainId]);

  return (
    <HqPageContent
      description={`${domain.emoji} ${domain.label} operations · ${tenant}`}
    >
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map((m) => (
          <CreamCard key={m.label} hover className="p-5">
            <div className="flex items-start justify-between gap-3">
              <div className={`rounded-xl p-2.5 ${m.soft}`}>
                <m.icon className={`h-5 w-5 ${m.iconColor}`} />
              </div>
              <span className="inline-flex items-center gap-1 rounded-full bg-accent-emerald-soft px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-accent-emerald">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent-emerald" />
                Live
              </span>
            </div>
            <p className="mt-4 text-sm text-ink-secondary">{m.label}</p>
            <p className="mt-1 text-2xl font-semibold text-ink-primary">{m.value}</p>
            <p className="mt-1 text-xs text-ink-tertiary">{m.delta}</p>
          </CreamCard>
        ))}
      </section>

      <div className="grid gap-6 lg:grid-cols-5">
        <CreamCard className="p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold text-ink-primary">Overview shortcuts</h2>
          <p className="mt-1 text-sm text-ink-secondary">
            Analytics & navigation — direct device control lives in Control Center.
          </p>
          <div className="mt-5 grid gap-3">
            <Link href="/control-center" prefetch className="hq-btn-primary w-full">
              <Radio className="h-4 w-4" />
              Open tactical control center
            </Link>
            <button type="button" className="hq-btn-soft w-full">
              <RefreshCw className="h-4 w-4" />
              Sync fleet telemetry
            </button>
            <Link href="/studio/automation" prefetch className="hq-btn-soft w-full">
              <Zap className="h-4 w-4 text-accent-indigo" />
              Automation Studio
            </Link>
            <Link href="/studio/missions" className="hq-btn-soft w-full">
              <MapPin className="h-4 w-4 text-accent-amber" />
              Open mission planner
            </Link>
            <Link href="/studio/firmware" className="hq-btn-soft w-full">
              <Cpu className="h-4 w-4 text-accent-violet" />
              Firmware studio
            </Link>
            <Link href="/developer/api-keys" className="hq-btn-soft w-full">
              <Shield className="h-4 w-4 text-accent-indigo" />
              API & webhooks
            </Link>
          </div>
        </CreamCard>

        <CreamCard className="overflow-hidden lg:col-span-3">
          <div className="border-b border-cream-border px-6 py-4">
            <h2 className="text-lg font-semibold text-ink-primary">Activity feed</h2>
            <p className="text-sm text-ink-secondary">Real-time platform events & system logs</p>
          </div>
          <ul className="divide-y divide-cream-border">
            {ACTIVITY.map((row) => (
              <li key={row.time + row.message} className="flex gap-4 px-6 py-3.5 text-sm">
                <span className="shrink-0 font-mono text-xs text-ink-tertiary">{row.time}</span>
                <span
                  className={`shrink-0 rounded-md px-2 py-0.5 text-[10px] font-semibold uppercase ${
                    row.level === "warn"
                      ? "bg-accent-amber-soft text-accent-amber"
                      : row.level === "success"
                        ? "bg-accent-emerald-soft text-accent-emerald"
                        : "bg-cream-muted text-ink-secondary"
                  }`}
                >
                  {row.level}
                </span>
                <span className="text-ink-primary">{row.message}</span>
              </li>
            ))}
          </ul>
        </CreamCard>
      </div>
    </HqPageContent>
  );
}
