"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { AdminCard } from "@/components/ui/AdminCard";
import { AdminDataTable } from "@/components/ui/AdminDataTable";
import {
  createAnnouncement,
  createPromoCode,
  fetchAnalyticsDeepDive,
  fetchAuditLog,
  fetchFeatureFlags,
  fetchHealthScores,
  fetchMqttStats,
  fetchPlatformSettings,
  fetchPromoCodes,
  fetchRateLimits,
  fetchSystemLogs,
  downloadAuditLogExport,
  fetchWatchList,
  formatIdr,
  listAnnouncements,
  updateFeatureFlag,
  updatePlatformSettings,
  type AnalyticsDeepDive,
  type AuditLogEntry,
  type FeatureFlag,
  type HealthScoreRow,
  type MqttStats,
} from "@/lib/api/super-admin-extended";

function scoreColor(score: number): string {
  if (score >= 70) return "text-emerald-600";
  if (score >= 40) return "text-amber-600";
  return "text-red-600";
}

export function AuditLogPanel() {
  const [rows, setRows] = useState<AuditLogEntry[]>([]);
  const [action, setAction] = useState("");
  useEffect(() => {
    void fetchAuditLog({ action: action || undefined }).then(setRows).catch(() => setRows([]));
  }, [action]);
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <input className="rounded-md border px-3 py-2 text-sm" placeholder="Filter action" value={action} onChange={(e) => setAction(e.target.value)} />
        <button type="button" className="rounded-md border px-3 py-2 text-sm" onClick={() => void downloadAuditLogExport()}>
          Export CSV
        </button>
      </div>
      <AdminDataTable
        rowKey={(r) => r.id}
        rows={rows}
        columns={[
          { key: "ts", header: "Time", render: (r) => new Date(r.timestamp).toLocaleString() },
          { key: "actor", header: "Actor", render: (r) => r.actor_label },
          { key: "action", header: "Action", render: (r) => r.action },
          { key: "target", header: "Target", render: (r) => r.target },
        ]}
      />
    </div>
  );
}

export function AnalyticsPanel() {
  const [data, setData] = useState<AnalyticsDeepDive | null>(null);
  useEffect(() => {
    void fetchAnalyticsDeepDive().then(setData).catch(() => setData(null));
  }, []);
  if (!data) return <p className="text-sm text-slate-500">Loading analytics…</p>;
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <AdminCard className="p-4"><p className="text-xs text-slate-500">ARPA</p><p className="text-xl font-semibold">{formatIdr(data.arpa_idr)}</p></AdminCard>
        <AdminCard className="p-4"><p className="text-xs text-slate-500">LTV (est.)</p><p className="text-xl font-semibold">{formatIdr(data.ltv_estimate_idr)}</p></AdminCard>
        <AdminCard className="p-4"><p className="text-xs text-slate-500">Cohort rows</p><p className="text-xl font-semibold">{data.cohort_retention.length}</p></AdminCard>
      </div>
      <AdminCard className="p-4">
        <h3 className="text-sm font-semibold">MRR trend</h3>
        <div className="mt-4 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.mrr_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => formatIdr(Number(v))} />
              <Bar dataKey="revenue_idr" fill="#1e40af" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </AdminCard>
      <AdminCard className="p-4">
        <h3 className="text-sm font-semibold">Churn by plan</h3>
        <ul className="mt-3 space-y-2 text-sm">
          {data.churn_by_plan.map((c) => (
            <li key={c.plan_code} className="flex justify-between"><span>{c.plan_code}</span><span>{c.churn_rate_percent}%</span></li>
          ))}
        </ul>
      </AdminCard>
    </div>
  );
}

export function HealthScorePanel() {
  const [rows, setRows] = useState<HealthScoreRow[]>([]);
  useEffect(() => {
    void fetchHealthScores().then(setRows).catch(() => setRows([]));
  }, []);
  return (
    <AdminDataTable
      rowKey={(r) => r.tenant_id}
      rows={rows}
      columns={[
        { key: "name", header: "Tenant", render: (r) => r.tenant_name },
        { key: "score", header: "Score", render: (r) => <span className={scoreColor(r.score)}>{r.score}</span> },
        { key: "risk", header: "Status", render: (r) => (r.at_risk ? <span className="text-red-600">At risk</span> : "Healthy") },
        { key: "devices", header: "Devices", render: (r) => r.device_count },
        {
          key: "actions",
          header: "Actions",
          render: (r) => (
            <Link href={`/tenants?highlight=${r.tenant_id}`} className="text-blue-800 hover:underline">Open</Link>
          ),
        },
      ]}
    />
  );
}

export function MqttMonitorPanel() {
  const [stats, setStats] = useState<MqttStats | null>(null);
  const refresh = useCallback(() => {
    void fetchMqttStats().then(setStats).catch(() => setStats(null));
  }, []);
  useEffect(() => {
    refresh();
    const id = window.setInterval(refresh, 5000);
    return () => window.clearInterval(id);
  }, [refresh]);
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <AdminCard className="p-4"><p className="text-xs text-slate-500">Connections</p><p className="text-2xl font-semibold">{stats?.connections ?? "—"}</p></AdminCard>
      <AdminCard className="p-4"><p className="text-xs text-slate-500">Status</p><p className="text-2xl font-semibold capitalize">{stats?.status ?? "…"}</p></AdminCard>
      <AdminCard className="p-4"><p className="text-xs text-slate-500">Errors</p><p className="text-2xl font-semibold">{stats?.errors ?? 0}</p></AdminCard>
    </div>
  );
}

export function RateLimitsPanel() {
  const [rows, setRows] = useState<Awaited<ReturnType<typeof fetchRateLimits>>>([]);
  useEffect(() => {
    void fetchRateLimits().then(setRows).catch(() => setRows([]));
  }, []);
  return (
    <AdminDataTable
      rowKey={(r) => r.tenant_id}
      rows={rows}
      columns={[
        { key: "t", header: "Tenant", render: (r) => r.tenant_name },
        { key: "api", header: "API calls", render: (r) => r.api_calls_period },
        { key: "mqtt", header: "MQTT msgs", render: (r) => r.mqtt_messages_period },
        { key: "quota", header: "Quota %", render: (r) => `${r.quota_usage_percent}%` },
        { key: "hits", header: "Limit hits", render: (r) => r.rate_limit_hits },
      ]}
    />
  );
}

export function SystemLogsPanel() {
  const [service, setService] = useState("api");
  const [level, setLevel] = useState("ERROR");
  const [lines, setLines] = useState<{ timestamp: string; level: string; message: string }[]>([]);
  useEffect(() => {
    const load = () => {
      void fetchSystemLogs({ service, level, lines: 50 }).then(setLines).catch(() => setLines([]));
    };
    load();
    const id = window.setInterval(load, 5000);
    return () => window.clearInterval(id);
  }, [service, level]);
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <select className="rounded border px-2 py-1 text-sm" value={service} onChange={(e) => setService(e.target.value)}>
          {["api", "web", "admin", "emqx"].map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select className="rounded border px-2 py-1 text-sm" value={level} onChange={(e) => setLevel(e.target.value)}>
          {["ERROR", "WARNING", "INFO"].map((l) => <option key={l} value={l}>{l}</option>)}
        </select>
      </div>
      <pre className="max-h-96 overflow-auto rounded-lg border bg-slate-950 p-4 font-mono text-xs text-emerald-400">
        {lines.map((l) => `${l.timestamp} [${l.level}] ${l.message}`).join("\n")}
      </pre>
    </div>
  );
}

export function TimelinePanel() {
  const [events, setEvents] = useState<AuditLogEntry[]>([]);
  useEffect(() => {
    void fetchAuditLog({ limit: 30 }).then(setEvents).catch(() => setEvents([]));
    const id = window.setInterval(() => {
      void fetchAuditLog({ limit: 30 }).then(setEvents).catch(() => setEvents([]));
    }, 8000);
    return () => window.clearInterval(id);
  }, []);
  return (
    <ul className="space-y-4 border-l-2 border-blue-200 pl-4">
      {events.map((e) => (
        <li key={e.id} className="relative">
          <span className="absolute -left-[1.35rem] top-1 h-3 w-3 rounded-full bg-blue-800" />
          <p className="text-sm font-medium">{e.action}</p>
          <p className="text-xs text-slate-500">{new Date(e.timestamp).toLocaleString()} · {e.actor_label}</p>
        </li>
      ))}
    </ul>
  );
}

export function AnnouncementsPanel() {
  const [items, setItems] = useState<Awaited<ReturnType<typeof listAnnouncements>>>([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const reload = () => void listAnnouncements().then(setItems).catch(() => setItems([]));
  useEffect(() => { reload(); }, []);
  return (
    <div className="space-y-4">
      <AdminCard className="space-y-2 p-4">
        <h3 className="text-sm font-semibold">New announcement</h3>
        <input className="w-full rounded border px-3 py-2 text-sm" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <textarea className="w-full rounded border px-3 py-2 text-sm" rows={3} placeholder="Body" value={body} onChange={(e) => setBody(e.target.value)} />
        <button type="button" className="rounded bg-blue-800 px-3 py-2 text-sm text-white" onClick={() => void createAnnouncement({ title, body, published: true }).then(reload)}>
          Publish
        </button>
      </AdminCard>
      <AdminDataTable rowKey={(r) => r.id} rows={items} columns={[
        { key: "t", header: "Title", render: (r) => r.title },
        { key: "type", header: "Type", render: (r) => r.announcement_type },
        { key: "pub", header: "Published", render: (r) => (r.published ? "Yes" : "Draft") },
      ]} />
    </div>
  );
}

export function PromoCodesPanel() {
  const [codes, setCodes] = useState<Awaited<ReturnType<typeof fetchPromoCodes>>>([]);
  useEffect(() => { void fetchPromoCodes().then(setCodes).catch(() => setCodes([])); }, []);
  return (
    <div className="space-y-4">
      <button type="button" className="rounded border px-3 py-2 text-sm" onClick={() => void createPromoCode({ code: `NEXT${Date.now() % 10000}`, discount_type: "percent", discount_value: 10, valid_plans: ["pro"] }).then(() => fetchPromoCodes().then(setCodes))}>
        Quick create sample code
      </button>
      <AdminDataTable rowKey={(c) => c.id} rows={codes} columns={[
        { key: "code", header: "Code", render: (c) => c.code },
        { key: "disc", header: "Discount", render: (c) => `${c.discount_value}${c.discount_type === "percent" ? "%" : " IDR"}` },
        { key: "used", header: "Used", render: (c) => `${c.used_count}${c.max_uses ? ` / ${c.max_uses}` : ""}` },
      ]} />
    </div>
  );
}

export function PlatformSettingsPanel() {
  const [sections, setSections] = useState<Record<string, Record<string, unknown>>>({});
  const [name, setName] = useState("");
  useEffect(() => {
    void fetchPlatformSettings().then((s) => {
      setSections(s.sections);
      const general = s.sections.general;
      if (general && typeof general.platform_name === "string") setName(general.platform_name);
    });
  }, []);
  return (
    <div className="space-y-4">
      <div className="flex gap-2 border-b">
        {["general", "email", "payment", "mqtt", "security", "notifications"].map((tab) => (
          <span key={tab} className="px-3 py-2 text-xs uppercase text-slate-500">{tab}</span>
        ))}
      </div>
      <AdminCard className="space-y-3 p-4">
        <label className="block text-sm">Platform name</label>
        <input className="w-full rounded border px-3 py-2 text-sm" value={name} onChange={(e) => setName(e.target.value)} />
        <button type="button" className="rounded bg-blue-800 px-3 py-2 text-sm text-white" onClick={() => void updatePlatformSettings({ general: { ...(sections.general ?? {}), platform_name: name } }).then(() => fetchPlatformSettings().then((s) => setSections(s.sections)))}>
          Save general
        </button>
      </AdminCard>
    </div>
  );
}

export function FeatureFlagsPanel() {
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  useEffect(() => { void fetchFeatureFlags().then(setFlags).catch(() => setFlags([])); }, []);
  return (
    <AdminDataTable
      rowKey={(f) => f.id}
      rows={flags}
      columns={[
        { key: "n", header: "Feature", render: (f) => f.name },
        { key: "d", header: "Description", render: (f) => f.description },
        { key: "g", header: "Global", render: (f) => (
          <button type="button" className="text-blue-800" onClick={() => void updateFeatureFlag(f.id, { enabled_global: !f.enabled_global }).then(() => fetchFeatureFlags().then(setFlags))}>
            {f.enabled_global ? "On" : "Off"}
          </button>
        )},
        { key: "r", header: "Rollout", render: (f) => `${f.rollout_percent}%` },
      ]}
    />
  );
}

export function FinanceExportPanel() {
  return (
    <AdminCard className="p-4">
      <p className="text-sm text-slate-600">Download paid invoices (last 30 days) as CSV for accounting.</p>
      <button
        type="button"
        className="mt-4 rounded bg-blue-800 px-4 py-2 text-sm text-white"
        onClick={() => void import("@/lib/api/super-admin-extended").then((m) => m.downloadFinanceExport())}
      >
        Download export
      </button>
    </AdminCard>
  );
}

export function WatchListSection() {
  const [items, setItems] = useState<Awaited<ReturnType<typeof fetchWatchList>>>([]);
  useEffect(() => { void fetchWatchList().then(setItems).catch(() => setItems([])); }, []);
  if (items.length === 0) return null;
  return (
    <AdminCard className="p-4">
      <h3 className="text-sm font-semibold">Watch list</h3>
      <ul className="mt-2 space-y-1 text-sm">
        {items.map((w) => (
          <li key={`${w.tenant_id}-${w.reason}`} className="flex justify-between">
            <span>{w.tenant_name}</span>
            <span className="text-slate-500">{w.reason}</span>
          </li>
        ))}
      </ul>
    </AdminCard>
  );
}

export function RevenueAnalyticsPanel() {
  const [data, setData] = useState<AnalyticsDeepDive | null>(null);
  useEffect(() => { void fetchAnalyticsDeepDive().then(setData).catch(() => setData(null)); }, []);
  if (!data) return <p className="text-sm text-slate-500">Loading…</p>;
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data.message_volume}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="messages" stroke="#1e40af" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ChurnPanel() {
  const [data, setData] = useState<AnalyticsDeepDive | null>(null);
  useEffect(() => { void fetchAnalyticsDeepDive().then(setData).catch(() => setData(null)); }, []);
  if (!data) return null;
  return (
    <AdminDataTable
      rowKey={(r) => r.plan_code}
      rows={data.churn_by_plan}
      columns={[
        { key: "p", header: "Plan", render: (r) => r.plan_code },
        { key: "s", header: "Subscribers", render: (r) => r.subscribers },
        { key: "c", header: "Churn %", render: (r) => r.churn_rate_percent },
      ]}
    />
  );
}
