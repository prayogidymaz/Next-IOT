"use client";

import { useCallback, useEffect, useState } from "react";

import { FadeInPage } from "@/components/motion/FadeInPage";
import { createWebhook, listWebhooks, testWebhook, type WebhookRecord } from "@/lib/api/webhooks";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/src/components/LoadingSkeleton";
import { ErrorState } from "@/src/components/ui/ErrorState";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { useHqToast } from "@/hooks/useHqToast";

export default function WebhooksPage() {
  const { showToast } = useHqToast();
  const [rows, setRows] = useState<WebhookRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [url, setUrl] = useState("https://example.com/webhook");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setRows(await listWebhooks());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Load failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function onCreate() {
    try {
      await createWebhook({ url, event_types: ["alarm.created"], secret_token: "change-me-16chars-min" });
      showToast("Webhook created", "success");
      await load();
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Create failed", "error");
    }
  }

  if (loading) return <TableSkeleton rows={5} />;
  if (error) return <ErrorState error={error} onRetry={() => void load()} />;

  return (
    <FadeInPage>
      <div className="container mx-auto space-y-4 px-4 py-4 md:px-6 lg:px-8">
        <div className="flex flex-wrap gap-2">
          <input
            className="min-w-[16rem] flex-1 rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            aria-label="Webhook URL"
          />
          <Button type="button" onClick={() => void onCreate()}>
            Add webhook
          </Button>
        </div>
        {rows.length === 0 ? (
          <EmptyState title="No webhooks" description="Register a URL to receive signed event payloads." />
        ) : (
          <ul className="divide-y divide-border rounded-xl border border-border bg-card">
            {rows.map((w) => (
              <li key={w.id} className="flex flex-wrap items-center justify-between gap-2 p-3 text-sm">
                <div className="min-w-0">
                  <p className="truncate font-medium text-foreground">{w.url}</p>
                  <p className="text-xs text-muted-foreground">{w.event_types_json.join(", ") || "all events"}</p>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    void testWebhook(w.id)
                      .then((r) => showToast(r.delivered ? "Delivered" : "Delivery failed", r.delivered ? "success" : "error"))
                      .catch((e: unknown) => showToast(e instanceof Error ? e.message : "Test failed", "error"))
                  }
                >
                  Test send
                </Button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </FadeInPage>
  );
}
