import { z } from "zod";

export const tokenResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
  role: z.string().optional(),
  email: z.string().optional(),
});

export const authUserSchema = z.object({
  user_id: z.string(),
  email: z.string(),
  role: z.string(),
  tenant_id: z.string(),
  permissions: z.array(z.string()),
});

export const registerResponseSchema = z.object({
  tokens: tokenResponseSchema,
});
