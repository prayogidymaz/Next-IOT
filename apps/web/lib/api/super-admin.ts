import { z } from "zod";

import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";

function bearer(): string {
  const prefix = `${ACCESS_TOKEN_COOKIE}=`;
  const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(prefix));
  const token = match ? decodeURIComponent(match.slice(prefix.length)) : null;
  if (!token) throw new Error("Belum masuk");
  return token;
}

const statsSchema = z.object({
  total_tenants: z.number(),
  active_tenants: z.number(),
  mrr_idr: z.number(),
  total_devices: z.number(),
});

export async function fetchSuperAdminStats() {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/stats`, {
    headers: { Authorization: `Bearer ${bearer()}` },
  });
  if (!res.ok) throw new Error(String(res.status));
  return statsSchema.parse(await res.json());
}
