"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { AgriFarmLayout } from "@/components/agriculture/AgriFarmLayout";
import { closeFarmValve, fetchFarmValves, openFarmValve } from "@/lib/agriculture/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

export default function IrrigationPage() {
  const farmId = String(useParams().id ?? "");
  const [valves, setValves] = useState<Awaited<ReturnType<typeof fetchFarmValves>>>([]);

  const reload = useCallback(() => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    void fetchFarmValves(token, farmId).then(setValves);
  }, [farmId]);

  useEffect(() => {
    reload();
  }, [reload]);

  const toggleValve = (valveId: string, state: string) => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    const action =
      state === "open" ? () => closeFarmValve(token, valveId) : () => openFarmValve(token, valveId, 15);
    void action().then(reload);
  };

  const usage = valves.map((v) => ({ name: v.name, liters: Math.random() * 500 }));

  return (
    <AgriFarmLayout farmId={farmId} title="Irrigation">
      <div className="grid gap-3 md:grid-cols-3">
        {valves.map((v) => (
          <div key={v.id} className="rounded-xl border p-4">
            <p className="font-medium">{v.name}</p>
            <p className={`text-xs ${v.current_state === "open" ? "text-emerald-600" : "text-slate-500"}`}>{v.current_state}</p>
            <p className="text-sm">Flow {v.flow_rate_lpm} L/min</p>
            <button
              type="button"
              className={`mt-3 w-full rounded px-3 py-2 text-sm text-white ${v.current_state === "open" ? "bg-slate-500" : "bg-emerald-600"}`}
              onClick={() => toggleValve(v.id, v.current_state)}
            >
              {v.current_state === "open" ? "Close" : "Open 15 min"}
            </button>
          </div>
        ))}
      </div>
      <div className="mt-6 h-64 rounded-xl border p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={usage}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="liters" fill="#10B981" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </AgriFarmLayout>
  );
}
