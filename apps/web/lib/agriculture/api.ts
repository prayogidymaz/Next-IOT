import { z } from "zod";

const farmSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  crop_type: z.string(),
  area_hectares: z.union([z.string(), z.number()]),
  location_address: z.string(),
});

export type AgriFarm = z.infer<typeof farmSchema>;

function apiBase(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
}

export async function fetchAgriFarms(token: string): Promise<AgriFarm[]> {
  const res = await fetch(`${apiBase()}/api/agriculture/farms`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(farmSchema).parse(await res.json());
}
