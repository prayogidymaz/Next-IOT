import { z } from "zod";

export const deviceResponseSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  name: z.string(),
  device_type: z.string(),
  device_category: z.string(),
  status: z.string(),
  last_seen_at: z.string().nullable(),
  profile_id: z.string().uuid().nullable(),
  metadata: z.array(z.object({ key: z.string(), value: z.string() })),
  created_at: z.string(),
});

export type DeviceResponse = z.infer<typeof deviceResponseSchema>;
