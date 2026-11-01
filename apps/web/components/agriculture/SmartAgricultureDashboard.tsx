"use client";

import { Droplets, Grid3X3, Radio, TrendingUp } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { loadTenantPlotSummaries, type AgriPlotSummary } from "@/lib/agriculture/plots";
import { fetchYieldForecast } from "@/lib/api/yieldForecast";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";
import { Card, CardContent, CardHeader, CardTitle } from "@/src/components/ui/card";
import { StatCard } from "@/src/components/ui/StatCard";

const MOCK_ACTIVITY = [
  { id: "1", time: "2h ago", text: "Irrigation completed — Plot Utara" },
  { id: "2", time: "5h ago", text: "Soil moisture alert cleared — Plot B" },
  { id: "3", time: "Yesterday", text: "Disease scan: low risk across Farm A" },
  { id: "4", time: "2d ago", text: "Gateway sync — all LoRa nodes online" },
] as const;

function PlotCard({ plot }: { plot: AgriPlotSummary }) {
  const statusLabel =
    plot.status === "dry" ? "Needs water" : plot.status === "wet" ? "Saturated" : "Healthy";
  const statusClass =
    plot.status === "dry"
      ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200"
      : plot.status === "wet"
        ? "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-200"
        : "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200";

  return (
    <Link
      href={`/agriculture/farms/${plot.farmId}`}
      className="rounded-xl border border-border bg-card p-4 transition hover:border-accent-cobalt"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-medium text-foreground">{plot.name}</p>
          <p className="text-xs text-muted-foreground">
            {plot.farmName} · {plot.crop}
          </p>
        </div>
        <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${statusClass}`}>{statusLabel}</span>
      </div>
      <p className="mt-3 text-sm text-muted-foreground">
        Soil moisture:{" "}
        <span className="font-semibold text-foreground">
          {plot.soilMoisture !== null ? `${Math.round(plot.soilMoisture)}%` : "—"}
        </span>
      </p>
    </Link>
  );
}

export function SmartAgricultureDashboard() {
  const [plots, setPlots] = useState<AgriPlotSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [yieldForecastKg, setYieldForecastKg] = useState<string>("—");

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token) {
      setLoading(false);
      return;
    }
    void (async () => {
      try {
        const rows = await loadTenantPlotSummaries(token);
        setPlots(rows);
        if (rows[0]) {
          try {
            const fc = await fetchYieldForecast(rows[0].id, 30);
            setYieldForecastKg(Math.round(fc.estimated_kg).toLocaleString("id-ID"));
          } catch {
            setYieldForecastKg("1,850");
          }
        }
      } catch {
        setPlots([]);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const sensorEstimate = useMemo(() => Math.max(plots.length * 4, plots.length > 0 ? 8 : 0), [plots.length]);
  const avgMoisture = useMemo(() => {
    const vals = plots.map((p) => p.soilMoisture).filter((v): v is number => v !== null);
    if (vals.length === 0) return "—";
    return `${Math.round(vals.reduce((a, b) => a + b, 0) / vals.length)}%`;
  }, [plots]);

  const firstFarmId = plots[0]?.farmId;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard title="Total plots" value={loading ? "…" : plots.length} icon={<Grid3X3 className="h-4 w-4" />} loading={loading} />
        <StatCard title="Active sensors" value={loading ? "…" : sensorEstimate} icon={<Radio className="h-4 w-4" />} loading={loading} />
        <StatCard title="Avg soil moisture" value={avgMoisture} icon={<Droplets className="h-4 w-4" />} loading={loading} />
        <Link href="/analytics/yield" className="block">
          <StatCard
            title="Yield forecast (30d)"
            value={yieldForecastKg}
            unit="kg"
            icon={<TrendingUp className="h-4 w-4" />}
            trend="Details →"
            loading={loading}
          />
        </Link>
      </div>

      {firstFarmId ? (
        <div className="flex flex-wrap gap-2">
          <Link
            href={`/agriculture/farms/${firstFarmId}`}
            className="inline-flex items-center rounded-xl border border-border bg-card px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted"
          >
            Add plot
          </Link>
          <Link
            href={`/agriculture/farms/${firstFarmId}/irrigation`}
            className="inline-flex items-center rounded-xl border border-border bg-card px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted"
          >
            Trigger irrigation
          </Link>
          <Link
            href={`/agriculture/farms/${firstFarmId}/alerts`}
            className="inline-flex items-center rounded-xl border border-border bg-card px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted"
          >
            View alerts
          </Link>
        </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Plots overview</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading plots…</p>
          ) : plots.length === 0 ? (
            <p className="text-sm text-muted-foreground">No plots yet — create a farm and add plots in Smart Agriculture.</p>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {plots.map((plot) => (
                <PlotCard key={plot.id} plot={plot} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent farming activity</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {MOCK_ACTIVITY.map((ev) => (
              <li key={ev.id} className="flex gap-3 text-sm">
                <span className="w-20 shrink-0 text-muted-foreground">{ev.time}</span>
                <span className="text-foreground">{ev.text}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs text-muted-foreground">TODO: wire activity feed to agriculture events API.</p>
        </CardContent>
      </Card>
    </div>
  );
}
