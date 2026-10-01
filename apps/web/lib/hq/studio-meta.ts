import { cache } from "react";

export type StudioMeta = {
  slug: string;
  deviceCount: number;
  pipelineCount: number;
  lastSync: string;
};

const STUDIO_META: Record<string, Omit<StudioMeta, "slug">> = {
  firmware: { deviceCount: 86, pipelineCount: 4, lastSync: "12s ago" },
  missions: { deviceCount: 18, pipelineCount: 7, lastSync: "8s ago" },
  automation: { deviceCount: 124, pipelineCount: 23, lastSync: "Live" },
};

export const loadStudioMeta = cache(async (slug: string): Promise<StudioMeta> => {
  await new Promise((r) => setTimeout(r, 0));
  const base = STUDIO_META[slug] ?? { deviceCount: 0, pipelineCount: 0, lastSync: "—" };
  return { slug, ...base };
});
