"use client";

import { useParams } from "next/navigation";
import { Bar, BarChart, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { AgriFarmLayout } from "@/components/agriculture/AgriFarmLayout";

export default function YieldPage() {
  const farmId = String(useParams().id ?? "");
  const yoy = [
    { m: "Jan", y2024: 400, y2025: 450, y2026: 480 },
    { m: "Jun", y2024: 900, y2025: 950, y2026: 1000 },
  ];
  const perPlot = [{ plot: "Blok A", kg: 1200 }, { plot: "Blok B", kg: 800 }];
  return (
    <AgriFarmLayout farmId={farmId} title="Yield">
      <div className="grid gap-4 md:grid-cols-4 text-sm">
        {["MTD kg", "Revenue IDR", "Price/kg", "Grade"].map((k) => (
          <div key={k} className="rounded border p-3"><p className="text-ink-tertiary">{k}</p><p className="text-xl font-semibold">—</p></div>
        ))}
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div className="h-56 rounded border p-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={yoy}><XAxis dataKey="m" /><YAxis /><Tooltip /><Line dataKey="y2024" stroke="#94A3B8" /><Line dataKey="y2025" stroke="#10B981" /><Line dataKey="y2026" stroke="#059669" /></LineChart>
          </ResponsiveContainer>
        </div>
        <div className="h-56 rounded border p-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={perPlot} layout="vertical"><XAxis type="number" /><YAxis type="category" dataKey="plot" width={60} /><Bar dataKey="kg" fill="#10B981" /></BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </AgriFarmLayout>
  );
}
