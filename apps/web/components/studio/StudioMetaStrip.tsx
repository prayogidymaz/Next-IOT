import { loadStudioMeta } from "@/lib/hq/studio-meta";

export async function StudioMetaStrip({ slug }: { slug: string }) {
  const meta = await loadStudioMeta(slug);
  return (
    <div className="flex flex-wrap gap-3 text-xs text-ink-secondary">
      <span className="rounded-full bg-cream-muted px-3 py-1">
        Devices in scope: <strong className="text-ink-primary">{meta.deviceCount}</strong>
      </span>
      <span className="rounded-full bg-cream-muted px-3 py-1">
        Pipelines: <strong className="text-ink-primary">{meta.pipelineCount}</strong>
      </span>
      <span className="rounded-full bg-accent-emerald-soft px-3 py-1 text-accent-emerald">
        Sync {meta.lastSync}
      </span>
    </div>
  );
}
