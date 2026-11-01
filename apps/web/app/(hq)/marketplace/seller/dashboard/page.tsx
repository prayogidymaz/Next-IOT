"use client";

import { useCallback, useEffect, useState } from "react";

import { FadeInPage } from "@/components/motion/FadeInPage";
import { fetchSellerDashboard, formatPriceIdr, type SellerDashboard } from "@/lib/api/workflowMarketplace";
import Link from "next/link";
import { CardSkeleton } from "@/src/components/LoadingSkeleton";
import { ErrorState } from "@/src/components/ui/ErrorState";

export default function SellerDashboardPage() {
  const [data, setData] = useState<SellerDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setData(await fetchSellerDashboard());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Load failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) return <CardSkeleton />;
  if (error) return <ErrorState error={error} onRetry={() => void load()} />;
  if (!data) return null;

  return (
    <FadeInPage>
      <div className="container mx-auto space-y-4 px-4 py-4 md:px-6 lg:px-8">
        <Link href="/marketplace/seller/payouts" className="text-sm text-muted-foreground hover:text-foreground">
          View payouts →
        </Link>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Stat label="Tier" value={data.tier} />
          <Stat label="Lifetime sales" value={formatPriceIdr(data.lifetime_sales_idr)} />
          <Stat label="Commission rate" value={`${data.commission_rate_percent}%`} />
          <Stat label="Pending payout" value={formatPriceIdr(data.pending_payout_idr)} />
        </div>
        {data.verified_badge ? <p className="text-sm text-emerald-600">Verified seller</p> : null}
      </div>
    </FadeInPage>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-xl font-semibold capitalize text-foreground">{value}</p>
    </div>
  );
}
