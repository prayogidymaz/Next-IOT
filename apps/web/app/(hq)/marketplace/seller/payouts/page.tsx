"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { FadeInPage } from "@/components/motion/FadeInPage";
import { fetchSellerPayouts, formatPriceIdr, type SellerPayout } from "@/lib/api/workflowMarketplace";
import { TableSkeleton } from "@/src/components/LoadingSkeleton";
import { ErrorState } from "@/src/components/ui/ErrorState";
import { EmptyState } from "@/src/components/ui/EmptyState";

export default function SellerPayoutsPage() {
  const [rows, setRows] = useState<SellerPayout[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setRows(await fetchSellerPayouts());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Load failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) return <TableSkeleton rows={5} />;
  if (error) return <ErrorState error={error} onRetry={() => void load()} />;

  return (
    <FadeInPage>
      <div className="container mx-auto space-y-4 px-4 py-4 md:px-6 lg:px-8">
        <Link href="/marketplace/seller/dashboard" className="text-sm text-muted-foreground hover:text-foreground">
          ← Seller dashboard
        </Link>
        {rows.length === 0 ? (
          <EmptyState title="No payouts yet" description="Monthly aggregation runs when sales exist." />
        ) : (
          <div className="overflow-x-auto rounded-xl border border-border bg-card">
            <table className="w-full text-sm">
              <thead className="border-b border-border text-left text-muted-foreground">
                <tr>
                  <th className="p-3">Period</th>
                  <th className="p-3">Gross</th>
                  <th className="p-3">Commission</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id} className="border-b border-border last:border-0">
                    <td className="p-3 text-foreground">{r.period_month}</td>
                    <td className="p-3">{formatPriceIdr(r.gross_sales_idr)}</td>
                    <td className="p-3">{formatPriceIdr(r.commission_idr)}</td>
                    <td className="p-3 capitalize text-muted-foreground">{r.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </FadeInPage>
  );
}
