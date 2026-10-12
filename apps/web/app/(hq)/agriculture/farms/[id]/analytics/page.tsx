"use client";

import { useParams } from "next/navigation";
import { Line, LineChart, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";

import { AgriFarmLayout } from "@/components/agriculture/AgriFarmLayout";

export default function AnalyticsPage() {
  const farmId = String(useParams().id ?? "");
  const water = Array.from({ length: 12 }, (_, i) => ({ d: `W${i + 1}`, v: 100 + i * 8 }));
  const env = Array.from({ length: 10 }, (_, i) => ({ d: i, temp: 26 + i * 0.2, humidity: 75 + i }));
  const cost = [{ cost: 10, yield: 20 }, { cost: 15, yield: 28 }];
  return (
    <AgriFarmLayout farmId={farmId} title="Analytics">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="h-52 rounded border p-2"><ResponsiveContainer width="100%" height="100%"><LineChart data={water}><XAxis dataKey="d" /><YAxis /><Tooltip /><Line dataKey="v" stroke="#10B981" /></LineChart></ResponsiveContainer></div>
        <div className="h-52 rounded border p-2"><ResponsiveContainer width="100%" height="100%"><LineChart data={env}><XAxis dataKey="d" /><YAxis /><Tooltip /><Line dataKey="temp" stroke="#F97316" /><Line dataKey="humidity" stroke="#3B82F6" /></LineChart></ResponsiveContainer></div>
        <div className="h-52 rounded border p-2"><ResponsiveContainer width="100%" height="100%"><ScatterChart><XAxis dataKey="cost" /><YAxis dataKey="yield" /><Tooltip /><Scatter data={cost} fill="#10B981" /></ScatterChart></ResponsiveContainer></div>
      </div>
    </AgriFarmLayout>
  );
}
