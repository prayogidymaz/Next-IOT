"use client";

import { useParams } from "next/navigation";

import { AgriFarmLayout } from "@/components/agriculture/AgriFarmLayout";

const STAGES = ["planting", "germination", "vegetative", "flowering", "fruiting", "harvesting", "post_harvest"];

export default function CalendarPage() {
  const farmId = String(useParams().id ?? "");
  return (
    <AgriFarmLayout farmId={farmId} title="Crop calendar">
      <p className="mb-4 rounded-full bg-emerald-100 px-3 py-1 text-sm inline-block">Current: vegetative · day 42</p>
      <div className="grid gap-2">
        {STAGES.map((stage, idx) => (
          <div key={stage} className="flex items-center gap-2">
            <span className="w-28 text-xs capitalize">{stage}</span>
            <div
              className={`h-6 flex-1 rounded ${idx < 3 ? "bg-emerald-500" : idx === 3 ? "bg-blue-500 animate-pulse" : "bg-slate-200"}`}
            />
          </div>
        ))}
      </div>
      <ul className="mt-6 list-disc space-y-1 pl-5 text-sm">
        <li>Pemupukan NPK dosis 300g per pohon</li>
        <li>Semprot fungisida preventif</li>
      </ul>
    </AgriFarmLayout>
  );
}
