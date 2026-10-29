"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Background, Controls, ReactFlow, ReactFlowProvider } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import {
  downloadMarketplaceTemplate,
  getMarketplaceTemplate,
  rateMarketplaceTemplate,
  unpublishMarketplaceTemplate,
  type WorkflowTemplateRecord,
} from "@/lib/api/workflowMarketplace";
import { useHqToast } from "@/hooks/useHqToast";
import { useHqShell } from "@/lib/hq/hq-shell-context";

function PreviewCanvas({ snapshot }: { snapshot: Record<string, unknown> }) {
  const def = snapshot.definition as { nodes?: { id: string; position?: { x: number; y: number }; data?: { label?: string } }[] } | undefined;
  const nodes =
    def?.nodes?.map((n, i) => ({
      id: n.id,
      type: "default",
      position: n.position ?? { x: i * 80, y: 40 },
      data: { label: n.data?.label ?? n.id },
    })) ?? [];
  return (
    <div className="h-48 rounded-lg border border-stone-200 bg-stone-50">
      <ReactFlow nodes={nodes} edges={[]} fitView nodesDraggable={false} nodesConnectable={false} elementsSelectable={false}>
        <Background />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}

type Props = { templateId: string };

export function MarketplaceDetailView({ templateId }: Props) {
  const router = useRouter();
  const { showToast } = useHqToast();
  const { tenant } = useHqShell();
  const [tpl, setTpl] = useState<WorkflowTemplateRecord | null>(null);
  const [downloaded, setDownloaded] = useState(false);
  const [rating, setRating] = useState(5);
  const [review, setReview] = useState("");

  const load = useCallback(async () => {
    setTpl(await getMarketplaceTemplate(templateId));
  }, [templateId]);

  useEffect(() => {
    void load().catch((e: unknown) => showToast(e instanceof Error ? e.message : "Load failed", "error"));
  }, [load, showToast]);

  const isAuthor = tpl?.author_tenant_id === tenant;

  async function onDownload() {
    try {
      const mesh = await downloadMarketplaceTemplate(templateId);
      setDownloaded(true);
      showToast("Template copied to workspace", "success");
      router.push(`/workflows/${mesh.id}`);
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Download failed", "error");
    }
  }

  async function onRate() {
    try {
      await rateMarketplaceTemplate(templateId, rating, review);
      showToast("Thanks for your review", "success");
      await load();
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Rating failed", "error");
    }
  }

  async function onUnpublish() {
    try {
      await unpublishMarketplaceTemplate(templateId);
      showToast("Unpublished", "success");
      router.push("/marketplace");
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Unpublish failed", "error");
    }
  }

  if (!tpl) return <p className="p-6 text-sm text-stone-500">Loading…</p>;

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <Link href="/marketplace" className="text-sm text-stone-600 hover:text-stone-900">
        ← Marketplace
      </Link>
      <header>
        <h1 className="text-2xl font-semibold text-stone-900">{tpl.name}</h1>
        <p className="mt-2 text-sm text-stone-600">{tpl.description}</p>
        <p className="mt-1 text-xs text-stone-500">
          {tpl.category} · {tpl.downloads_count} downloads · ★ {tpl.rating_avg.toFixed(1)} ({tpl.rating_count})
        </p>
      </header>

      <ReactFlowProvider>
        <PreviewCanvas snapshot={tpl.snapshot_json} />
      </ReactFlowProvider>

      <div className="flex flex-wrap gap-2">
        <button type="button" className="rounded-lg bg-stone-900 px-4 py-2 text-sm text-white" onClick={() => void onDownload()}>
          Download to My Workspace
        </button>
        {isAuthor ? (
          <button type="button" className="rounded-lg border border-red-300 px-4 py-2 text-sm text-red-700" onClick={() => void onUnpublish()}>
            Unpublish
          </button>
        ) : null}
      </div>

      <section className="rounded-xl border border-stone-200 p-4">
        <h2 className="text-sm font-semibold text-stone-800">Ratings</h2>
        <p className="text-sm text-stone-600">Average {tpl.rating_avg.toFixed(1)} from {tpl.rating_count} reviews</p>
        {downloaded ? (
          <div className="mt-4 space-y-2">
            <label className="block text-xs text-stone-600">
              Your rating (1–5)
              <input type="number" min={1} max={5} className="ml-2 w-16 rounded border px-2 py-1 text-sm" value={rating} onChange={(e) => setRating(Number(e.target.value))} />
            </label>
            <textarea className="w-full rounded border px-3 py-2 text-sm" rows={2} value={review} onChange={(e) => setReview(e.target.value)} placeholder="Review (optional)" />
            <button type="button" className="rounded bg-stone-800 px-3 py-1.5 text-sm text-white" onClick={() => void onRate()}>
              Submit rating
            </button>
          </div>
        ) : (
          <p className="mt-2 text-xs text-stone-500">Download this template to leave a rating.</p>
        )}
      </section>
    </div>
  );
}
