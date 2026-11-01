"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { loadTenantPlotSummaries, type AgriPlotSummary } from "@/lib/agriculture/plots";
import { fetchYieldForecast, type YieldForecastResult } from "@/lib/api/yieldForecast";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/src/components/ui/card";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { Label } from "@/src/components/ui/label";

const HORIZONS = [7, 30, 90] as const;

function formatRisk(code: string): string {
  return code.replace(/_/g, " ");
}

function buildChartSeries(forecast: YieldForecastResult): { day: string; kg: number }[] {
  const days = forecast.horizon_days;
  const end = forecast.estimated_kg;
  const start = end * 0.82;
  return Array.from({ length: days }, (_, i) => ({
    day: `D+${i + 1}`,
    kg: Math.round((start + ((end - start) * i) / Math.max(days - 1, 1)) * 10) / 10,
  }));
}

export function YieldForecastView() {
  const [plots, setPlots] = useState<AgriPlotSummary[]>([]);
  const [plotId, setPlotId] = useState("");
  const [horizon, setHorizon] = useState<number>(30);
  const [forecast, setForecast] = useState<YieldForecastResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token) {
      setLoading(false);
      return;
    }
    void loadTenantPlotSummaries(token)
      .then((rows) => {
        setPlots(rows);
        if (rows[0]) setPlotId(rows[0].id);
      })
      .catch(() => setPlots([]))
      .finally(() => setLoading(false));
  }, []);

  const loadForecast = useCallback(async (pid: string, days: number) => {
    if (!pid) return;
    setError(null);
    setLoading(true);
    try {
      setForecast(await fetchYieldForecast(pid, days));
    } catch (e) {
      setForecast(null);
      setError(e instanceof Error ? e.message : "Forecast unavailable");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!plotId) return;
    void loadForecast(plotId, horizon);
  }, [plotId, horizon, loadForecast]);

  const chartData = useMemo(() => (forecast ? buildChartSeries(forecast) : []), [forecast]);

  const selectClass =
    "h-10 rounded-lg border border-border bg-background px-3 text-sm text-foreground";

  if (!loading && plots.length === 0) {
    return (
      <EmptyState
        title="No plots for forecast"
        description="Add farms and plots in Smart Agriculture first."
      />
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-end">
            <div className="space-y-2">
              <Label htmlFor="yield-plot">Select plot</Label>
              <select
                id="yield-plot"
                className={selectClass}
                value={plotId}
                onChange={(e) => setPlotId(e.target.value)}
              >
                {plots.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.farmName})
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="yield-horizon">Horizon</Label>
              <select
                id="yield-horizon"
                className={selectClass}
                value={String(horizon)}
                onChange={(e) => setHorizon(Number(e.target.value))}
              >
                {HORIZONS.map((d) => (
                  <option key={d} value={d}>
                    {d} days
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <Card>
        <CardHeader>
          <CardTitle>Yield prediction</CardTitle>
          {forecast ? (
            <CardDescription>
              Estimated harvest: {forecast.estimated_kg.toLocaleString("id-ID")} kg (CI:{" "}
              {forecast.confidence_interval[0].toLocaleString("id-ID")}–
              {forecast.confidence_interval[1].toLocaleString("id-ID")} kg) · Model {forecast.model_version}
            </CardDescription>
          ) : null}
        </CardHeader>
        <CardContent>
          {loading && !forecast ? (
            <p className="text-sm text-muted-foreground">Loading forecast…</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} unit=" kg" />
                <Tooltip />
                <Line type="monotone" dataKey="kg" stroke="hsl(var(--foreground))" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
          <p className="mt-2 text-xs text-muted-foreground">
            Chart shows projected trend toward horizon endpoint (API returns point estimate + CI).
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Risk factors</CardTitle>
        </CardHeader>
        <CardContent>
          {forecast && forecast.risk_factors.length > 0 ? (
            <ul className="list-inside list-disc space-y-1 text-sm text-foreground">
              {forecast.risk_factors.map((risk) => (
                <li key={risk}>{formatRisk(risk)}</li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted-foreground">No elevated risk factors for this horizon.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
