"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { HoverLiftCard } from "@/components/motion/HoverLiftCard";
import { FadeInPage } from "@/components/motion/FadeInPage";
import { SiteMapView } from "@/components/sites/SiteMapView";
import { listSites, type SiteRecord } from "@/lib/api/sites";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { ErrorState } from "@/src/components/ui/ErrorState";
import { GridSkeleton } from "@/src/components/LoadingSkeleton";

export function SitesListView() {
  const [sites, setSites] = useState<SiteRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setSites(await listSites());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load sites");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) return <GridSkeleton count={6} />;
  if (error) return <ErrorState error={error} onRetry={() => void load()} />;
  if (sites.length === 0) {
    return <EmptyState title="No sites yet" description="Create a site via POST /api/v1/sites or seed data." />;
  }

  return (
    <FadeInPage>
      <div className="container mx-auto space-y-4 px-4 md:px-6 lg:px-8">
        <SiteMapView sites={sites} />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {sites.map((s) => (
          <HoverLiftCard key={s.id}>
            <Link
              href={`/sites/${s.id}`}
              className="block rounded-xl border border-border bg-card p-4 text-sm transition hover:border-primary/40"
            >
              <p className="font-semibold text-foreground">{s.name}</p>
              <p className="text-xs text-muted-foreground">{s.slug} · {s.timezone}</p>
              {typeof s.location_json.address === "string" ? (
                <p className="mt-2 truncate text-xs text-muted-foreground">{s.location_json.address}</p>
              ) : null}
            </Link>
          </HoverLiftCard>
        ))}
      </div>
      </div>
    </FadeInPage>
  );
}
