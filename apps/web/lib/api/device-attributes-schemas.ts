import { z } from "zod";

export const deviceAttributeItemSchema = z.object({
  key: z.string(),
  scope: z.string(),
  value: z.unknown(),
  updated_at: z.string(),
  updated_by_user_id: z.string().nullable(),
  updated_source: z.string(),
});

export const deviceAttributeListSchema = z.object({
  items: z.array(deviceAttributeItemSchema),
});

export type DeviceAttributeItem = z.infer<typeof deviceAttributeItemSchema>;
