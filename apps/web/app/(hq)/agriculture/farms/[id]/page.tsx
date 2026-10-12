"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

const TABS = ["overview", "sensors", "irrigation", "alerts", "calendar", "yield", "analytics"] as const;

export default function FarmDetailPage() {
  const params = useParams();
  const farmId = String(params.id ?? "");
  return (
    <div className="space-y-4 p-6">
      <Link href="/agriculture" className="text-sm text-accent-cobalt">← Agriculture hub</Link>
      <h1 className="text-xl font-semibold">Farm {farmId.slice(0, 8)}</h1>
      <div className="flex flex-wrap gap-2 text-sm">
        {TABS.map((t) => (
          <Link
            key={t}
            href={`/agriculture/farms/${farmId}/${t === "overview" ? "" : t}`.replace(/\/$/, "") || `/agriculture/farms/${farmId}`}
            className="rounded-full border px-3 py-1 capitalize"
          >
            {t}
          </Link>
        ))}
      </div>
      <p className="text-sm text-ink-secondary">
        Peta interaktif (plot, sensor LoRa, gateway, valve) — hubungkan ke API{" "}
        <code className="text-xs">/api/agriculture/farms/{farmId}/overview</code>
      </p>
    </div>
  );
}
