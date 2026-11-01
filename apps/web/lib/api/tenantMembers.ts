import { z } from "zod";

import { apiFetch, apiUrl } from "@/src/lib/api/client";

const memberSchema = z.object({
  user_id: z.string().uuid(),
  email: z.string(),
  role: z.string(),
  is_active: z.boolean(),
  created_at: z.string(),
});

const inviteSchema = z.object({
  id: z.string().uuid(),
  email: z.string(),
  role: z.string(),
  status: z.string(),
  expires_at: z.string(),
  created_at: z.string(),
});

export type TenantMember = z.infer<typeof memberSchema>;
export type TenantInvitation = z.infer<typeof inviteSchema>;

export async function listTenantMembers(tenantId: string, search?: string): Promise<TenantMember[]> {
  const q = search ? `?search=${encodeURIComponent(search)}` : "";
  const res = await apiFetch(apiUrl(`/api/v1/tenants/${tenantId}/members${q}`));
  if (!res.ok) throw new Error(`Members list failed (${res.status})`);
  return z.array(memberSchema).parse(await res.json());
}

export async function inviteTenantMember(tenantId: string, email: string, role: string): Promise<TenantInvitation> {
  const res = await apiFetch(apiUrl(`/api/v1/tenants/${tenantId}/members/invite`), {
    method: "POST",
    body: JSON.stringify({ email, role }),
  });
  if (!res.ok) throw new Error(`Invite failed (${res.status})`);
  return inviteSchema.parse(await res.json());
}

export async function listTenantInvitations(tenantId: string): Promise<TenantInvitation[]> {
  const res = await apiFetch(apiUrl(`/api/v1/tenants/${tenantId}/members/invitations`));
  if (!res.ok) throw new Error(`Invitations failed (${res.status})`);
  return z.array(inviteSchema).parse(await res.json());
}

export async function cancelTenantInvitation(tenantId: string, inviteId: string): Promise<void> {
  const res = await apiFetch(apiUrl(`/api/v1/tenants/${tenantId}/members/invitations/${inviteId}`), { method: "DELETE" });
  if (!res.ok) throw new Error(`Cancel failed (${res.status})`);
}

export async function resendTenantInvitation(tenantId: string, inviteId: string): Promise<TenantInvitation> {
  const res = await apiFetch(apiUrl(`/api/v1/tenants/${tenantId}/members/invitations/${inviteId}/resend`), { method: "POST" });
  if (!res.ok) throw new Error(`Resend failed (${res.status})`);
  return inviteSchema.parse(await res.json());
}
