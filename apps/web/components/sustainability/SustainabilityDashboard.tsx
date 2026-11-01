"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { FadeInPage } from "@/components/motion/FadeInPage";
import {
  esgPdfUrl,
  fetchCarbonTrend,
  fetchCurrentEsg,
  fetchWaterUsage,
  generateEsg,
  type CarbonPoint,
  type EsgScorecard,
  type WaterPoint,
} from "@/lib/api/sustainability";
import { readApiAccessToken } from "@/lib/auth/api-headers";
import { Button } from "@/components/ui/button";
import { ChartSkeleton } from "@/src/components/LoadingSkeleton";
import { ErrorState } from "@/src/components/ui/ErrorState";
import { EmptyState } from "@/src/components/ui/EmptyState";

function num(v: string | number): number {
  return typeof v === "number" ? v : Number.parseFloat(v);
}

export function SustainabilityDashboard() {
  const [carbon, setCarbon] = useState<CarbonPoint[]>([]);
  const [water, setWater] = useState<WaterPoint[]>([]);
  const [esg, setEsg] = useState<EsgScorecard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [c, w, e] = await Promise.all([fetchCarbonTrend(), fetchWaterUsage(), fetchCurrentEsg()]);
      setCarbon(c);
      setWater(w);
      setEsg(e);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Load failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const carbonChart = useMemo(
    () =>
      [...carbon]
        .reverse()
        .slice(-30)
        .map((p) => ({ t: p.recorded_at.slice(0, 10), kg: num(p.co2_equivalent_kg) })),
    [carbon],
  );

  const waterByPlot = useMemo(() => {
    const map = new Map<string, number>();
    for (const w of water) {
      const key = w.plot_id ?? "unassigned";
      map.set(key, (map.get(key) ?? 0) + num(w.liters_used));
    }
    return [...map.entries()].map(([plot, liters]) => ({ plot: plot.slice(0, 8), liters }));
  }, [water]);

  async function onGenerate() {
    const month = new Date().toISOString().slice(0, 7);
    try {
      setEsg(await generateEsg(month));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Generate failed");
    }
  }

  function onExportPdf() {
    if (!esg) return;
    const token = readApiAccessToken();
    void fetch(esgPdfUrl(esg.id), { headers: { Authorization: `Bearer ${token ?? ""}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `esg-${esg.period_month}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
      })
      .catch(() => setError("PDF export failed"));
  }

  if (loading) {
    return (
      <div className="container mx-auto space-y-4 px-4 md:px-6 lg:px-8">
        <ChartSkeleton />
        <ChartSkeleton />
      </div>
    );
  }
  if (error) return <ErrorState error={error} onRetry={() => void load()} />;

  return (
    <FadeInPage>
      <div className="container mx-auto space-y-6 px-4 py-4 md:px-6 lg:px-8">
        <div className="flex flex-wrap items-center gap-2">
          <Button type="button" variant="outline" onClick={() => void onGenerate()}>
            Generate ESG (this month)
          </Button>
          {esg ? (
            <Button type="button" onClick={onExportPdf}>
              Export PDF
            </Button>
          ) : null}
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="rounded-xl border border-border bg-card p-4 lg:col-span-2">
            <p className="mb-2 text-sm font-medium text-foreground">Carbon trend (kg CO₂e)</p>
            {carbonChart.length === 0 ? (
              <EmptyState title="No carbon data" description="Entries appear when telemetry or manual logs exist." />
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={carbonChart}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="t" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="kg" stroke="hsl(var(--primary))" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
          <div className="rounded-xl border border-border bg-card p-4">
            <p className="text-sm font-medium text-foreground">ESG grade</p>
            {esg ? (
              <div className="mt-4 text-center">
                <p className="text-5xl font-bold text-foreground">{esg.overall_grade}</p>
                <p className="mt-2 text-xs text-muted-foreground">
                  E {num(esg.environmental_score)} · S {num(esg.social_score)} · G {num(esg.governance_score)}
                </p>
                <p className="text-xs text-muted-foreground">{esg.period_month}</p>
              </div>
            ) : (
              <EmptyState title="No scorecard" description="Generate a monthly scorecard to see your grade." />
            )}
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-4">
          <p className="mb-2 text-sm font-medium text-foreground">Water usage by plot (L)</p>
          {waterByPlot.length === 0 ? (
            <EmptyState title="No water data" description="Irrigation events and manual entries will show here." />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={waterByPlot}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="plot" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="liters" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </FadeInPage>
  );
}
