import { z } from "zod";

export const firmwareReleaseSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  version: z.string(),
  target_device_category: z.string(),
  file_url: z.string(),
  checksum_sha256: z.string(),
  status: z.string(),
  created_at: z.string(),
});

export type FirmwareRelease = z.infer<typeof firmwareReleaseSchema>;

export const otaRolloutSchema = z.object({
  id: z.string().uuid(),
  device_id: z.string().uuid(),
  device_name: z.string(),
  status: z.string(),
  reported_at: z.string().nullable(),
  created_at: z.string(),
});

export type OtaRollout = z.infer<typeof otaRolloutSchema>;

export const otaPublishResponseSchema = z.object({
  release: firmwareReleaseSchema,
  targeted_devices: z.number(),
  rollouts_created: z.number(),
});
