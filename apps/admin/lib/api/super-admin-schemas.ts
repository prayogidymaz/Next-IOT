import { z } from "zod";

export const platformStatsSchema = z.object({
  total_tenants: z.number(),
  active_tenants: z.number(),
  trial_subscriptions: z.number(),
  active_subscriptions: z.number(),
  total_devices: z.number(),
  mrr_idr: z.number(),
  arr_idr: z.number().optional(),
  revenue_mtd_idr: z.number(),
  messages_today: z.number().optional(),
});

export const tenantAdminItemSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  slug: z.string(),
  is_active: z.boolean(),
  plan_code: z.string().nullable(),
  subscription_status: z.string().nullable(),
  device_count: z.number(),
  user_count: z.number(),
  created_at: z.string(),
});

export const tenantDetailSchema = tenantAdminItemSchema.extend({
  trial_ends_at: z.string().nullable(),
  audit_entries: z.array(
    z.object({
      id: z.string().uuid(),
      action: z.string(),
      detail: z.record(z.string(), z.unknown()),
      created_at: z.string(),
    }),
  ),
});

export const revenueSchema = z.object({
  mrr_idr: z.number(),
  arr_idr: z.number(),
  by_plan: z.record(z.string(), z.number()),
  growth_12m: z.array(
    z.object({
      month: z.string(),
      revenue_idr: z.number(),
    }),
  ),
});

export const invoiceSchema = z.object({
  id: z.string().uuid(),
  invoice_number: z.string(),
  period_start: z.string(),
  period_end: z.string(),
  subtotal_idr: z.number(),
  tax_idr: z.number(),
  total_idr: z.number(),
  status: z.string(),
  due_date: z.string(),
  paid_at: z.string().nullable(),
  pdf_url: z.string().nullable(),
});

export const systemHealthSchema = z.object({
  api: z.string(),
  database: z.string(),
  redis: z.string(),
  emqx: z.string(),
  scheduler: z.string(),
  mqtt_subscriber: z.string(),
  mqtt_publisher: z.string(),
  checked_at: z.string(),
});

export type PlatformStats = z.infer<typeof platformStatsSchema>;
export type TenantAdminItem = z.infer<typeof tenantAdminItemSchema>;
export type TenantDetail = z.infer<typeof tenantDetailSchema>;
export type RevenueReport = z.infer<typeof revenueSchema>;
export type PlatformInvoice = z.infer<typeof invoiceSchema>;
export type SystemHealth = z.infer<typeof systemHealthSchema>;
