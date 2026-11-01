import { fetchAgriFarms, fetchFarmMap } from "@/lib/agriculture/api";

export type AgriPlotSummary = {
  id: string;
  name: string;
  farmId: string;
  farmName: string;
  crop: string;
  soilMoisture: number | null;
  status: "ok" | "dry" | "wet";
};

export function plotStatusFromMoisture(moisture: number | null): AgriPlotSummary["status"] {
  if (moisture === null) return "ok";
  if (moisture < 40) return "dry";
  if (moisture > 75) return "wet";
  return "ok";
}

export async function loadTenantPlotSummaries(token: string, maxFarms = 8): Promise<AgriPlotSummary[]> {
  const farms = await fetchAgriFarms(token);
  const plots: AgriPlotSummary[] = [];
  await Promise.all(
    farms.slice(0, maxFarms).map(async (farm) => {
      try {
        const map = await fetchFarmMap(token, farm.id);
        for (const plot of map.plots) {
          plots.push({
            id: plot.id,
            name: plot.name,
            farmId: farm.id,
            farmName: farm.name,
            crop: farm.crop_type,
            soilMoisture: plot.moisture_pct,
            status: plotStatusFromMoisture(plot.moisture_pct),
          });
        }
      } catch {
        /* skip farm */
      }
    }),
  );
  return plots;
}
