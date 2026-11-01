"use client";

import { useCallback, useEffect, useState } from "react";

import { HqPageContent } from "@/components/hq/HqPageContent";
import { SlideFadeModal } from "@/components/motion/SlideFadeModal";
import { Button } from "@/components/ui/button";
import {
  cancelTenantInvitation,
  inviteTenantMember,
  listTenantInvitations,
  listTenantMembers,
  resendTenantInvitation,
  type TenantInvitation,
  type TenantMember,
} from "@/lib/api/tenantMembers";
import { fetchAuthMe } from "@/lib/auth/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";
import { Card, CardContent, CardHeader, CardTitle } from "@/src/components/ui/card";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { TableSkeleton } from "@/src/components/LoadingSkeleton";

const ROLE_MAP: Record<string, string> = {
  owner: "tenant_admin",
  admin: "tenant_admin",
  member: "operator",
  viewer: "viewer",
};

export function MembersPanel() {
  const [tenantId, setTenantId] = useState<string | null>(null);
  const [rows, setRows] = useState<TenantMember[]>([]);
  const [invites, setInvites] = useState<TenantInvitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("member");

  const load = useCallback(async (tid: string) => {
    setLoading(true);
    try {
      const [members, pending] = await Promise.all([listTenantMembers(tid), listTenantInvitations(tid)]);
      setRows(members);
      setInvites(pending);
      setError(null);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load members");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token) {
      setLoading(false);
      return;
    }
    void fetchAuthMe(token)
      .then((me) => {
        setTenantId(me.tenant_id);
        return load(me.tenant_id);
      })
      .catch(() => setLoading(false));
  }, [load]);

  async function submitInvite() {
    if (!tenantId) return;
    await inviteTenantMember(tenantId, email, ROLE_MAP[role] ?? "viewer");
    setModalOpen(false);
    setEmail("");
    await load(tenantId);
  }

  return (
    <HqPageContent>
      <div className="mb-4 flex justify-end">
        <Button type="button" onClick={() => setModalOpen(true)}>
          + Invite member
        </Button>
      </div>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <Card>
        <CardHeader>
          <CardTitle>Members & roles</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <TableSkeleton rows={4} />
          ) : rows.length === 0 ? (
            <EmptyState title="No members" description="Invite teammates to collaborate on this tenant." />
          ) : (
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-muted/40 text-xs uppercase text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3">Email</th>
                    <th className="px-4 py-3">Role</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Joined</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {rows.map((m) => (
                    <tr key={m.user_id}>
                      <td className="px-4 py-3 font-medium text-foreground">{m.email}</td>
                      <td className="px-4 py-3 text-muted-foreground">{m.role}</td>
                      <td className="px-4 py-3">{m.is_active ? "Active" : "Inactive"}</td>
                      <td className="px-4 py-3 text-muted-foreground">{new Date(m.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Pending invitations</CardTitle>
        </CardHeader>
        <CardContent>
          {invites.length === 0 ? (
            <p className="text-sm text-muted-foreground">No pending invites.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {invites.map((inv) => (
                <li key={inv.id} className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border px-3 py-2">
                  <span className="text-foreground">
                    {inv.email} · {inv.role} · {inv.status}
                  </span>
                  <span className="flex gap-2">
                    <Button type="button" size="sm" variant="outline" onClick={() => tenantId && void resendTenantInvitation(tenantId, inv.id).then(() => load(tenantId))}>
                      Resend
                    </Button>
                    <Button type="button" size="sm" variant="ghost" onClick={() => tenantId && void cancelTenantInvitation(tenantId, inv.id).then(() => load(tenantId))}>
                      Cancel
                    </Button>
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <SlideFadeModal open={modalOpen} onClose={() => setModalOpen(false)}>
        <p className="font-medium text-foreground">Invite member</p>
        <input className="mt-3 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email@company.com" />
        <select className="mt-2 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm" value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="owner">Owner</option>
          <option value="admin">Admin</option>
          <option value="member">Member</option>
          <option value="viewer">Viewer</option>
        </select>
        <Button type="button" className="mt-4 w-full" onClick={() => void submitInvite()}>
          Send invite
        </Button>
      </SlideFadeModal>
    </HqPageContent>
  );
}
