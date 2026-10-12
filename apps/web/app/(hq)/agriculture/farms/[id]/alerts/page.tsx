"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { AgriFarmLayout } from "@/components/agriculture/AgriFarmLayout";
import {
  acknowledgeDiseaseAlert,
  fetchDiseaseAlerts,
  fetchDiseaseRiskForecast,
  resolveDiseaseAlert,
  snoozeDiseaseAlert,
} from "@/lib/agriculture/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

const RISK_COLOR: Record<string, string> = {
  critical: "bg-red-600",
  high: "bg-orange-500",
  medium: "bg-amber-400",
  low: "bg-slate-300",
};

export default function AlertsPage() {
  const farmId = String(useParams().id ?? "");
  const [alerts, setAlerts] = useState<Awaited<ReturnType<typeof fetchDiseaseAlerts>>>([]);
  const [forecast, setForecast] = useState<{ day: string; score: number }[]>([]);

  const reload = () => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    void fetchDiseaseAlerts(token, farmId).then(setAlerts);
    void fetchDiseaseRiskForecast(token, farmId).then((rows) =>
      setForecast(
        rows.map((r) => ({
          day: r.date ?? `D${r.day_index + 1}`,
          score: r.risk_level === "high" ? 80 : r.risk_level === "medium" ? 55 : 25,
        })),
      ),
    );
  };

  useEffect(() => {
    reload();
  }, [farmId]);

  const run = (fn: (token: string, id: string) => Promise<void>, alertId: string) => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    void fn(token, alertId).then(reload);
  };

  return (
    <AgriFarmLayout farmId={farmId} title="Disease alerts">
      <div className="space-y-3">
        {alerts.map((a) => (
          <div key={a.id} className="rounded-xl border p-4">
            <span className={`rounded px-2 py-0.5 text-xs text-white ${RISK_COLOR[a.risk_level] ?? "bg-slate-400"}`}>
              {a.risk_level}
            </span>
            <h3 className="mt-2 font-semibold">{a.disease_name}</h3>
            <p className="text-sm text-ink-secondary">{a.action_recommended}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                type="button"
                className="rounded border px-2 py-1 text-xs"
                onClick={() => run(acknowledgeDiseaseAlert, a.id)}
              >
                Acknowledge
              </button>
              <button
                type="button"
                className="rounded border px-2 py-1 text-xs"
                onClick={() => run(resolveDiseaseAlert, a.id)}
              >
                Resolve
              </button>
              <button
                type="button"
                className="rounded border px-2 py-1 text-xs"
                onClick={() => run(snoozeDiseaseAlert, a.id)}
              >
                Snooze 24h
              </button>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 h-64 rounded-xl border p-4">
        <p className="mb-2 text-sm font-medium">7-day risk forecast</p>
        <ResponsiveContainer width="100%" height="90%">
          <LineChart data={forecast}>
            <XAxis dataKey="day" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Line dataKey="score" stroke="#10B981" name="Risk score" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </AgriFarmLayout>
  );
}
