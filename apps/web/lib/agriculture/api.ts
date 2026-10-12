import { z } from "zod";

const farmSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  crop_type: z.string(),
  area_hectares: z.union([z.string(), z.number()]),
  location_address: z.string(),
  location_lat: z.union([z.string(), z.number(), z.null()]).optional(),
  location_lng: z.union([z.string(), z.number(), z.null()]).optional(),
});

export type AgriFarm = z.infer<typeof farmSchema>;

const mapDataSchema = z.object({
  farm: farmSchema.extend({
    tenant_id: z.string().uuid(),
    owner_whatsapp: z.string().optional(),
    metadata: z.record(z.unknown()).optional(),
    created_at: z.string().optional(),
    updated_at: z.string().optional(),
  }),
  plots: z.array(
    z.object({
      id: z.string().uuid(),
      name: z.string(),
      polygon: z.record(z.unknown()),
      moisture_pct: z.number().nullable(),
    }),
  ),
  sensors: z.array(
    z.object({
      id: z.string().uuid(),
      name: z.string(),
      sensor_type: z.string(),
      lat: z.number().nullable(),
      lng: z.number().nullable(),
      last_moisture: z.number().nullable(),
    }),
  ),
  gateways: z.array(
    z.object({
      id: z.string().uuid(),
      name: z.string(),
      lat: z.number().nullable(),
      lng: z.number().nullable(),
    }),
  ),
  valves: z.array(
    z.object({
      id: z.string().uuid(),
      name: z.string(),
      plot_id: z.string().uuid(),
      lat: z.number().nullable(),
      lng: z.number().nullable(),
      current_state: z.string(),
    }),
  ),
  bounds: z.object({
    south: z.number(),
    north: z.number(),
    west: z.number(),
    east: z.number(),
  }),
});

export type FarmMapData = z.infer<typeof mapDataSchema>;

function apiBase(): string {
  if (typeof window !== "undefined" && !process.env.NEXT_PUBLIC_API_BASE_URL) {
    return "";
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}`, Accept: "application/json" };
}

export async function fetchAgriFarms(token: string): Promise<AgriFarm[]> {
  const res = await fetch(`${apiBase()}/api/agriculture/farms`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(farmSchema).parse(await res.json());
}

export async function fetchFarm(token: string, farmId: string): Promise<AgriFarm> {
  const res = await fetch(`${apiBase()}/api/agriculture/farms/${farmId}`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error(String(res.status));
  return farmSchema.passthrough().parse(await res.json()) as AgriFarm;
}

export async function fetchFarmMap(token: string, farmId: string): Promise<FarmMapData> {
  const res = await fetch(`${apiBase()}/api/agriculture/farms/${farmId}/map-data`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error(String(res.status));
  return mapDataSchema.parse(await res.json());
}

export async function fetchFarmOverview(token: string, farmId: string) {
  const res = await fetch(`${apiBase()}/api/agriculture/farms/${farmId}/overview`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error(String(res.status));
  return res.json() as Promise<{
    sensor_count: number;
    active_alerts: number;
    gateway_count: number;
    avg_soil_moisture_pct: number | null;
  }>;
}

export async function fetchDiseaseAlerts(token: string, farmId: string) {
  const res = await fetch(`${apiBase()}/api/agriculture/farms/${farmId}/disease-alerts`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error(String(res.status));
  return z
    .array(
      z.object({
        id: z.string().uuid(),
        plot_id: z.string().uuid(),
        disease_name: z.string(),
        risk_level: z.string(),
        factors: z.record(z.unknown()),
        action_recommended: z.string(),
        predicted_at: z.string(),
      }),
    )
    .parse(await res.json());
}

export async function fetchSensorReadings(token: string, sensorId: string, range: string) {
  const res = await fetch(
    `${apiBase()}/api/agriculture/sensors/${sensorId}/readings?range=${encodeURIComponent(range)}`,
    { headers: authHeaders(token) },
  );
  if (!res.ok) throw new Error(String(res.status));
  return z.array(z.object({ ts: z.string(), value: z.number(), metric: z.string() })).parse(await res.json());
}

export async function fetchFarmValves(token: string, farmId: string) {
  const res = await fetch(`${apiBase()}/api/agriculture/farms/${farmId}/valves`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error(String(res.status));
  return z
    .array(
      z.object({
        id: z.string().uuid(),
        name: z.string(),
        plot_id: z.string().uuid(),
        current_state: z.string(),
        flow_rate_lpm: z.union([z.string(), z.number()]),
      }),
    )
    .parse(await res.json());
}

export async function fetchNotificationSettings(token: string, farmId: string) {
  const res = await fetch(`${apiBase()}/api/agriculture/farms/${farmId}/notification-settings`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error(String(res.status));
  return z
    .object({
      disease_alerts: z.boolean(),
      irrigation: z.boolean(),
      battery: z.boolean(),
      weather: z.boolean(),
      harvest: z.boolean(),
      whatsapp_number: z.string(),
    })
    .parse(await res.json());
}

export async function saveNotificationSettings(
  token: string,
  farmId: string,
  body: Record<string, boolean | string>,
) {
  const res = await fetch(`${apiBase()}/api/agriculture/farms/${farmId}/notification-settings`, {
    method: "PUT",
    headers: { ...authHeaders(token), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(String(res.status));
  return res.json();
}

export async function testFarmNotification(token: string, farmId: string): Promise<{ sent: boolean }> {
  const res = await fetch(`${apiBase()}/api/agriculture/farms/${farmId}/notification-settings/test`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error(String(res.status));
  return z.object({ sent: z.boolean() }).parse(await res.json());
}

export async function acknowledgeDiseaseAlert(token: string, alertId: string): Promise<void> {
  const res = await fetch(`${apiBase()}/api/agriculture/disease-alerts/${alertId}/acknowledge`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error(String(res.status));
}

export async function resolveDiseaseAlert(token: string, alertId: string): Promise<void> {
  const res = await fetch(`${apiBase()}/api/agriculture/disease-alerts/${alertId}/resolve`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error(String(res.status));
}

export async function snoozeDiseaseAlert(token: string, alertId: string): Promise<void> {
  const res = await fetch(`${apiBase()}/api/agriculture/disease-alerts/${alertId}/snooze`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error(String(res.status));
}

export async function openFarmValve(token: string, valveId: string, durationMinutes: number): Promise<void> {
  const res = await fetch(`${apiBase()}/api/agriculture/valves/${valveId}/open`, {
    method: "POST",
    headers: { ...authHeaders(token), "Content-Type": "application/json" },
    body: JSON.stringify({ duration_minutes: durationMinutes }),
  });
  if (!res.ok) throw new Error(String(res.status));
}

export async function closeFarmValve(token: string, valveId: string): Promise<void> {
  const res = await fetch(`${apiBase()}/api/agriculture/valves/${valveId}/close`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error(String(res.status));
}

export async function fetchDiseaseRiskForecast(token: string, farmId: string) {
  const res = await fetch(`${apiBase()}/api/agriculture/farms/${farmId}/disease-risk-forecast`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error(String(res.status));
  return z
    .array(
      z.object({
        day_index: z.number(),
        risk_level: z.string(),
        date: z.string().optional(),
      }),
    )
    .parse(await res.json());
}

/** Indonesia mobile: 08xx, +62, or 62 prefix. */
export function isValidIndonesiaWhatsApp(number: string): boolean {
  const digits = number.replace(/\s/g, "");
  return /^(\+62|62|0)8[1-9]\d{7,11}$/.test(digits);
}
