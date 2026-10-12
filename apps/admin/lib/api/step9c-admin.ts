import { z } from "zod";

import { getApiBaseUrl } from "@/lib/auth/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

function headers(): HeadersInit {
  const token = readAccessTokenFromDocument();
  if (!token) throw new Error("Belum masuk");
  return { Accept: "application/json", Authorization: `Bearer ${token}` };
}

const emailTemplateSchema = z.object({
  id: z.string().uuid(),
  code: z.string(),
  name: z.string(),
  subject: z.string(),
  body_html: z.string(),
  body_text: z.string().nullable(),
  is_active: z.boolean(),
  updated_at: z.string(),
  variables: z.array(z.object({ name: z.string(), description: z.string() })),
});

export type EmailTemplate = z.infer<typeof emailTemplateSchema>;

export async function fetchEmailTemplates(): Promise<EmailTemplate[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/email-templates`, { headers: headers() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(emailTemplateSchema).parse(await res.json());
}

export async function updateEmailTemplate(code: string, body: Record<string, unknown>): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/email-templates/${code}`, {
    method: "PUT",
    headers: { ...headers(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function previewEmailTemplate(code: string, sample_variables: Record<string, string>) {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/email-templates/${code}/preview`, {
    method: "POST",
    headers: { ...headers(), "Content-Type": "application/json" },
    body: JSON.stringify({ sample_variables }),
  });
  if (!res.ok) throw new Error(String(res.status));
  return z.object({ subject: z.string(), body_html: z.string() }).parse(await res.json());
}

const ticketSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid().nullable(),
  subject: z.string(),
  category: z.string(),
  priority: z.string(),
  status: z.string(),
  assigned_to: z.string().uuid().nullable(),
  updated_at: z.string(),
});

export async function fetchSupportTickets(params: { status?: string }): Promise<z.infer<typeof ticketSchema>[]> {
  const qs = params.status ? `?status=${encodeURIComponent(params.status)}` : "";
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/support-tickets${qs}`, { headers: headers() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(ticketSchema).parse(await res.json());
}

const ticketDetailSchema = ticketSchema.extend({
  description: z.string(),
  messages: z.array(
    z.object({
      id: z.string().uuid(),
      author_id: z.string().uuid().nullable(),
      is_internal: z.boolean(),
      body: z.string(),
      attachments: z.array(z.string()),
      created_at: z.string(),
    }),
  ),
});

export type SupportTicketDetail = z.infer<typeof ticketDetailSchema>;

export async function fetchSupportTicket(id: string): Promise<SupportTicketDetail> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/support-tickets/${id}`, { headers: headers() });
  if (!res.ok) throw new Error(String(res.status));
  return ticketDetailSchema.parse(await res.json());
}

export async function assignSupportTicket(id: string, user_id: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/support-tickets/${id}/assign`, {
    method: "POST",
    headers: { ...headers(), "Content-Type": "application/json" },
    body: JSON.stringify({ user_id }),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function setSupportTicketStatus(id: string, status: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/support-tickets/${id}/status`, {
    method: "POST",
    headers: { ...headers(), "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function postSupportTicketMessage(
  id: string,
  body: { body: string; is_internal: boolean },
): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/support-tickets/${id}/messages`, {
    method: "POST",
    headers: { ...headers(), "Content-Type": "application/json" },
    body: JSON.stringify({ ...body, attachments: [] }),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function fetchSupportStats() {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/support-tickets/stats`, { headers: headers() });
  if (!res.ok) throw new Error(String(res.status));
  return z
    .object({
      open: z.number(),
      in_progress: z.number(),
      waiting_customer: z.number(),
      resolved_today: z.number(),
      avg_resolution_hours: z.number(),
    })
    .parse(await res.json());
}

const partnerSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  tier: z.string(),
  status: z.string(),
  referral_code: z.string(),
  commission_percent: z.number(),
  contact_email: z.string(),
  company_name: z.string(),
  joined_at: z.string(),
});

export async function fetchPartners(): Promise<z.infer<typeof partnerSchema>[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/partners`, { headers: headers() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(partnerSchema).parse(await res.json());
}

export async function fetchPartnerReferrals(partnerId: string) {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/partners/${partnerId}/referrals`, {
    headers: headers(),
  });
  if (!res.ok) throw new Error(String(res.status));
  return z
    .array(
      z.object({
        id: z.string().uuid(),
        tenant_id: z.string().uuid(),
        referred_at: z.string(),
        total_revenue_idr: z.number(),
        total_commission_idr: z.number(),
      }),
    )
    .parse(await res.json());
}

export async function fetchPartnerCommissions(partnerId: string) {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/partners/${partnerId}/commissions`, {
    headers: headers(),
  });
  if (!res.ok) throw new Error(String(res.status));
  return z
    .array(
      z.object({
        id: z.string().uuid(),
        period_month: z.string(),
        total_commission_idr: z.number(),
        status: z.string(),
        paid_at: z.string().nullable(),
      }),
    )
    .parse(await res.json());
}

export async function calculatePartnerCommission(partnerId: string, period_month: string) {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/partners/${partnerId}/commissions/calculate`, {
    method: "POST",
    headers: { ...headers(), "Content-Type": "application/json" },
    body: JSON.stringify({ period_month }),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function markPartnerCommissionPaid(partnerId: string, commissionId: string) {
  const res = await fetch(
    `${getApiBaseUrl()}/api/v1/super-admin/partners/${partnerId}/commissions/${commissionId}/mark-paid`,
    { method: "POST", headers: headers() },
  );
  if (!res.ok) throw new Error(await res.text());
}

export async function createPartner(body: { name: string; contact_email?: string; tier?: string }) {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/partners`, {
    method: "POST",
    headers: { ...headers(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return partnerSchema.parse(await res.json());
}

const backupSchema = z.object({
  id: z.string().uuid(),
  backup_type: z.string(),
  size_bytes: z.number(),
  status: z.string(),
  started_at: z.string(),
  completed_at: z.string().nullable(),
});

export async function fetchBackups() {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/backups`, { headers: headers() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(backupSchema).parse(await res.json());
}

export async function triggerBackup(backup_type: string) {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/backups/trigger`, {
    method: "POST",
    headers: { ...headers(), "Content-Type": "application/json" },
    body: JSON.stringify({ backup_type }),
  });
  if (!res.ok) throw new Error(await res.text());
  return backupSchema.parse(await res.json());
}

const impersonationSessionSchema = z.object({
  id: z.string().uuid(),
  super_admin_user_id: z.string().uuid().nullable(),
  tenant_id: z.string().uuid().nullable(),
  started_at: z.string(),
  ended_at: z.string().nullable(),
  action_count: z.number(),
  duration_seconds: z.number().nullable(),
});

export async function fetchImpersonationSessions() {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/impersonation/sessions`, { headers: headers() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(impersonationSessionSchema).parse(await res.json());
}
