import { z } from "zod";

export const deviceCredentialPublicSchema = z.object({
  id: z.string().uuid(),
  device_id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  credential_type: z.string(),
  client_id: z.string(),
  is_active: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
  last_connected_at: z.string().nullable(),
  rotated_at: z.string().nullable(),
});

export const deviceCredentialCreateSchema = deviceCredentialPublicSchema.extend({
  access_token: z.string(),
  client_secret: z.string().nullable().optional(),
});

export type DeviceCredentialPublic = z.infer<typeof deviceCredentialPublicSchema>;
export type DeviceCredentialCreate = z.infer<typeof deviceCredentialCreateSchema>;
