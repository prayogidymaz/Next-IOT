"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { FadeInPage } from "@/components/motion/FadeInPage";
import { getSite, getSiteReport, listSitePlots, type PlotRecord, type SiteRecord } from "@/lib/api/sites";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { ErrorState } from "@/src/components/ui/ErrorState";
import { CardSkeleton, GridSkeleton } from "@/src/components/LoadingSkeleton";

type Props = { siteId: string };

export function SiteDetailView({ siteId }: Props) {
  const [site, setSite] = useState<SiteRecord | null>(null);
  const [plots, setPlots] = useState<PlotRecord[]>([]);
  const [kpi, setKpi] = useState<{ plot_count: number; total_area_hectares: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, p, r] = await Promise.all([getSite(siteId), listSitePlots(siteId), getSiteReport(siteId, 30)]);
      setSite(s);
      setPlots(p);
      setKpi({ plot_count: r.plot_count, total_area_hectares: r.total_area_hectares });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load site");
    } finally {
      setLoading(false);
    }
  }, [siteId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) {
    return (
      <div className="container mx-auto space-y-4 px-4 md:px-6 lg:px-8">
        <CardSkeleton />
        <GridSkeleton count={3} />
      </div>
    );
  }
  if (error) return <ErrorState error={error} onRetry={() => void load()} />;
  if (!site) return null;

  return (
    <FadeInPage>
      <div className="container mx-auto space-y-6 px-4 py-4 md:px-6 lg:px-8">
        <Link href="/sites" className="text-sm text-muted-foreground hover:text-foreground">
          ← Sites
        </Link>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          <div className="rounded-xl border border-border bg-card p-4">
            <p className="text-xs text-muted-foreground">Plots</p>
            <p className="text-2xl font-semibold text-foreground">{kpi?.plot_count ?? 0}</p>
          </div>
          <div className="rounded-xl border border-border bg-card p-4">
            <p className="text-xs text-muted-foreground">Total area (ha)</p>
            <p className="text-2xl font-semibold text-foreground">{kpi?.total_area_hectares.toFixed(2) ?? "0"}</p>
          </div>
          <div className="rounded-xl border border-border bg-card p-4">
            <p className="text-xs text-muted-foreground">Timezone</p>
            <p className="text-lg font-medium text-foreground">{site.timezone}</p>
          </div>
        </div>
        {plots.length === 0 ? (
          <EmptyState title="No plots" description="Add plots under this site from the API." />
        ) : (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
            {plots.map((p) => (
              <Link
                key={p.id}
                href={`/sites/${siteId}/plots/${p.id}`}
                className="rounded-xl border border-border bg-card p-4 text-sm hover:border-primary/40"
              >
                <p className="font-medium text-foreground">{p.name}</p>
                <p className="text-xs text-muted-foreground">
                  {p.crop_type || "—"} · {String(p.area_hectares)} ha
                </p>
              </Link>
            ))}
          </div>
        )}
      </div>
    </FadeInPage>
  );
}
