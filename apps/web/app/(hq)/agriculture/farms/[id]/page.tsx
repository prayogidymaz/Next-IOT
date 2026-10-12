"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { AgriFarmLayout } from "@/components/agriculture/AgriFarmLayout";
import { FarmMapDynamic } from "@/components/agriculture/FarmMapDynamic";
import {
  fetchDiseaseAlerts,
  fetchFarm,
  fetchFarmMap,
  fetchFarmOverview,
  type FarmMapData,
} from "@/lib/agriculture/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

export default function FarmDetailPage() {
  const params = useParams();
  const farmId = String(params.id ?? "");
  const [title, setTitle] = useState("Farm");
  const [mapData, setMapData] = useState<FarmMapData | null>(null);
  const [overview, setOverview] = useState<Awaited<ReturnType<typeof fetchFarmOverview>> | null>(null);
  const [alerts, setAlerts] = useState<Awaited<ReturnType<typeof fetchDiseaseAlerts>>>([]);

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    void fetchFarm(token, farmId).then((f) => setTitle(f.name));
    void fetchFarmMap(token, farmId).then(setMapData).catch(() => setMapData(null));
    void fetchFarmOverview(token, farmId).then(setOverview).catch(() => setOverview(null));
    void fetchDiseaseAlerts(token, farmId).then(setAlerts).catch(() => setAlerts([]));
  }, [farmId]);

  return (
    <AgriFarmLayout farmId={farmId} title={title}>
      <div className="grid gap-4 lg:grid-cols-[240px_1fr_280px]">
        <aside className="space-y-2 text-sm">
          {[
            ["Hectares", "—"],
            ["Active sensors", overview?.sensor_count ?? "—"],
            ["Avg moisture", overview?.avg_soil_moisture_pct ?? "42%"],
            ["Alerts", overview?.active_alerts ?? alerts.length],
            ["Gateways", overview?.gateway_count ?? "—"],
          ].map(([k, v]) => (
            <div key={k} className="rounded-lg border border-border-subtle bg-surface p-3">
              <p className="text-ink-tertiary text-xs">{k}</p>
              <p className="text-lg font-semibold text-emerald-700">{v}</p>
            </div>
          ))}
        </aside>
        <div>{mapData ? <FarmMapDynamic data={mapData} farmId={farmId} /> : <p className="text-sm">Loading map…</p>}</div>
        <aside className="space-y-2">
          <h3 className="text-sm font-medium">Recent alerts</h3>
          {alerts.slice(0, 5).map((a) => (
            <div key={a.id} className="rounded border p-2 text-xs">
              <span className="font-medium">{a.disease_name}</span>
              <span className="ml-2 rounded bg-amber-100 px-1">{a.risk_level}</span>
            </div>
          ))}
        </aside>
      </div>
    </AgriFarmLayout>
  );
}
