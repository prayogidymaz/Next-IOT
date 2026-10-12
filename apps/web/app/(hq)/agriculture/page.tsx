"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { fetchAgriFarms, type AgriFarm } from "@/lib/agriculture/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

export default function AgricultureHubPage() {
  const [farms, setFarms] = useState<AgriFarm[]>([]);
  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    void fetchAgriFarms(token).then(setFarms).catch(() => setFarms([]));
  }, []);
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-semibold">Smart Agriculture</h1>
      <p className="text-sm text-ink-secondary">Monitor kebun LoRa — tanpa SIM card, baterai 1–3 tahun.</p>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {farms.map((f) => (
          <Link
            key={f.id}
            href={`/agriculture/farms/${f.id}`}
            className="rounded-xl border border-border-subtle bg-surface p-4 hover:border-accent-cobalt"
          >
            <p className="font-medium">{f.name}</p>
            <p className="text-xs text-ink-tertiary">{f.crop_type} · {f.area_hectares} ha</p>
            <p className="text-xs text-ink-secondary">{f.location_address}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
