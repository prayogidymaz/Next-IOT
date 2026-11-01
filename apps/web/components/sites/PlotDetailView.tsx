"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { listSitePlots, type PlotRecord } from "@/lib/api/sites";
import { ErrorState } from "@/src/components/ui/ErrorState";
import { CardSkeleton } from "@/src/components/LoadingSkeleton";

type Props = { siteId: string; plotId: string };

export function PlotDetailView({ siteId, plotId }: Props) {
  const [plot, setPlot] = useState<PlotRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const rows = await listSitePlots(siteId);
      setPlot(rows.find((p) => p.id === plotId) ?? null);
      if (!rows.find((p) => p.id === plotId)) setError("Plot not found");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Load failed");
    } finally {
      setLoading(false);
    }
  }, [siteId, plotId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) return <CardSkeleton />;
  if (error || !plot) return <ErrorState error={error ?? "Not found"} onRetry={() => void load()} />;

  return (
    <div className="container mx-auto space-y-4 px-4 py-4 md:px-6 lg:px-8">
      <Link href={`/sites/${siteId}`} className="text-sm text-muted-foreground hover:text-foreground">
        ← Site
      </Link>
      <div className="rounded-xl border border-border bg-card p-6 text-sm md:text-base">
        <p className="text-lg font-semibold text-foreground">{plot.name}</p>
        <dl className="mt-4 grid grid-cols-1 gap-2 md:grid-cols-2">
          <div>
            <dt className="text-muted-foreground">Crop</dt>
            <dd className="text-foreground">{plot.crop_type || "—"}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Area (ha)</dt>
            <dd className="text-foreground">{String(plot.area_hectares)}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Soil</dt>
            <dd className="text-foreground">{plot.soil_type || "—"}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Planting</dt>
            <dd className="text-foreground">{plot.planting_date ?? "—"}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}
