"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { format } from "date-fns";

import { AgriFarmLayout } from "@/components/agriculture/AgriFarmLayout";
import { fetchSensorReadings } from "@/lib/agriculture/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

export default function SensorDetailPage() {
  const params = useParams();
  const farmId = String(params.id ?? "");
  const sensorId = String(params.sensorId ?? "");
  const [range, setRange] = useState("24h");
  const [points, setPoints] = useState<{ ts: string; value: number }[]>([]);

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    void fetchSensorReadings(token, sensorId, range).then((rows) =>
      setPoints(rows.map((r) => ({ ts: r.ts, value: r.value }))),
    );
  }, [sensorId, range]);

  return (
    <AgriFarmLayout farmId={farmId} title={`Sensor ${sensorId.slice(0, 8)}`}>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border p-4">
          <div className="mb-2 flex gap-2 text-sm">
            {(["24h", "7d", "30d"] as const).map((r) => (
              <button
                key={r}
                type="button"
                className={`rounded px-2 py-1 ${range === r ? "bg-emerald-600 text-white" : "bg-slate-100"}`}
                onClick={() => setRange(r)}
              >
                {r}
              </button>
            ))}
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={points}>
              <XAxis dataKey="ts" tickFormatter={(v) => format(new Date(v), "HH:mm")} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#10B981" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="space-y-3">
          <div className="rounded-xl border p-4">
            <p className="text-sm text-ink-tertiary">Battery</p>
            <p className="text-3xl font-semibold">3.7 V</p>
          </div>
          <div className="rounded-xl border p-4">
            <p className="text-sm text-ink-tertiary">Signal RSSI</p>
            <p className="text-3xl font-semibold">-92 dBm</p>
          </div>
        </div>
      </div>
    </AgriFarmLayout>
  );
}
