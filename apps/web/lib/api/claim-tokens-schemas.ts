import { z } from "zod";

export const claimTokenSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  claim_token: z.string(),
  device_name: z.string(),
  device_type: z.string(),
  device_category: z.string(),
  profile_id: z.string().uuid().nullable(),
  expires_at: z.string(),
  claimed_at: z.string().nullable(),
  claimed_device_id: z.string().uuid().nullable(),
  created_at: z.string(),
  created_by_user_id: z.string().uuid().nullable(),
  qr_code_url: z.string(),
});

export type ClaimToken = z.infer<typeof claimTokenSchema>;

export const claimTokenCreateSchema = z.object({
  device_name: z.string(),
  device_type: z.string(),
  device_category: z.string(),
  profile_id: z.string().uuid().nullable().optional(),
  ttl_hours: z.number(),
});

export type ClaimTokenCreateInput = z.infer<typeof claimTokenCreateSchema>;
