"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { AdminCard } from "@/components/ui/AdminCard";
import { AdminDataTable } from "@/components/ui/AdminDataTable";
import {
  assignSupportTicket,
  calculatePartnerCommission,
  createPartner,
  fetchBackups,
  fetchEmailTemplates,
  fetchImpersonationSessions,
  fetchPartnerCommissions,
  fetchPartnerReferrals,
  fetchPartners,
  fetchSupportStats,
  fetchSupportTicket,
  fetchSupportTickets,
  markPartnerCommissionPaid,
  postSupportTicketMessage,
  setSupportTicketStatus,
  triggerBackup,
  type EmailTemplate,
} from "@/lib/api/step9c-admin";
import { readUserIdFromDocumentCookie } from "@/lib/auth/token-role";

export function EmailTemplatesListPanel() {
  const [rows, setRows] = useState<EmailTemplate[]>([]);
  useEffect(() => {
    void fetchEmailTemplates().then(setRows).catch(() => setRows([]));
  }, []);
  return (
    <AdminDataTable
      rowKey={(r) => r.id}
      rows={rows}
      columns={[
        { key: "code", header: "Code", render: (r) => r.code },
        { key: "name", header: "Name", render: (r) => r.name },
        { key: "active", header: "Active", render: (r) => (r.is_active ? "Yes" : "No") },
        { key: "upd", header: "Updated", render: (r) => new Date(r.updated_at).toLocaleString() },
        {
          key: "edit",
          header: "",
          render: (r) => (
            <Link className="text-blue-800 hover:underline" href={`/email-templates/${r.code}`}>Edit</Link>
          ),
        },
      ]}
    />
  );
}

export function SupportTicketsListPanel() {
  const [stats, setStats] = useState<Awaited<ReturnType<typeof fetchSupportStats>> | null>(null);
  const [rows, setRows] = useState<Awaited<ReturnType<typeof fetchSupportTickets>>>([]);
  const [status, setStatus] = useState("");
  useEffect(() => {
    void fetchSupportStats().then(setStats).catch(() => setStats(null));
  }, []);
  useEffect(() => {
    void fetchSupportTickets({ status: status || undefined }).then(setRows).catch(() => setRows([]));
  }, [status]);
  return (
    <div className="space-y-4">
      {stats ? (
        <div className="grid gap-3 md:grid-cols-5">
          {(
            [
              ["Open", stats.open],
              ["In progress", stats.in_progress],
              ["Waiting", stats.waiting_customer],
              ["Resolved today", stats.resolved_today],
              ["Avg hours", stats.avg_resolution_hours],
            ] as const
          ).map(([label, val]) => (
            <AdminCard key={label} className="p-3 text-sm">
              <p className="text-slate-500">{label}</p>
              <p className="text-xl font-semibold">{val}</p>
            </AdminCard>
          ))}
        </div>
      ) : null}
      <select className="rounded border px-2 py-1 text-sm" value={status} onChange={(e) => setStatus(e.target.value)}>
        <option value="">All status</option>
        <option value="open">Open</option>
        <option value="in_progress">In progress</option>
        <option value="resolved">Resolved</option>
      </select>
      <AdminDataTable
        rowKey={(r) => r.id}
        rows={rows}
        columns={[
          { key: "sub", header: "Subject", render: (r) => r.subject },
          { key: "pri", header: "Priority", render: (r) => r.priority },
          { key: "st", header: "Status", render: (r) => r.status },
          {
            key: "lnk",
            header: "",
            render: (r) => <Link href={`/support-tickets/${r.id}`} className="text-blue-800">Open</Link>,
          },
        ]}
      />
    </div>
  );
}

export function PartnersListPanel() {
  const [rows, setRows] = useState<Awaited<ReturnType<typeof fetchPartners>>>([]);
  const reload = () => void fetchPartners().then(setRows).catch(() => setRows([]));
  useEffect(() => { reload(); }, []);
  return (
    <div className="space-y-3">
      <button
        type="button"
        className="rounded bg-blue-800 px-3 py-2 text-sm text-white"
        onClick={() => void createPartner({ name: `Partner ${Date.now() % 1000}` }).then(reload)}
      >
        New partner
      </button>
      <AdminDataTable
        rowKey={(r) => r.id}
        rows={rows}
        columns={[
          { key: "n", header: "Name", render: (r) => r.name },
          { key: "t", header: "Tier", render: (r) => r.tier },
          { key: "c", header: "Code", render: (r) => <code className="text-xs">{r.referral_code}</code> },
          { key: "s", header: "Status", render: (r) => r.status },
          { key: "lnk", header: "", render: (r) => <Link href={`/partners/${r.id}`} className="text-blue-800">Detail</Link> },
        ]}
      />
    </div>
  );
}

export function BackupListPanel() {
  const [rows, setRows] = useState<Awaited<ReturnType<typeof fetchBackups>>>([]);
  const reload = () => void fetchBackups().then(setRows).catch(() => setRows([]));
  useEffect(() => { reload(); }, []);
  return (
    <div className="space-y-4">
      <AdminCard className="p-4 text-sm text-slate-600">
        Daily full backup · 7-day retention · local storage <code className="text-xs">/var/backups/next-iot</code>
      </AdminCard>
      <button type="button" className="rounded bg-blue-800 px-3 py-2 text-sm text-white" onClick={() => void triggerBackup("full").then(reload)}>
        Trigger backup now
      </button>
      <AdminDataTable
        rowKey={(r) => r.id}
        rows={rows}
        columns={[
          { key: "t", header: "Type", render: (r) => r.backup_type },
          { key: "s", header: "Status", render: (r) => r.status },
          { key: "sz", header: "Size", render: (r) => `${r.size_bytes} B` },
          { key: "at", header: "Started", render: (r) => new Date(r.started_at).toLocaleString() },
        ]}
      />
    </div>
  );
}

export function SupportTicketDetailPanel({ ticketId }: { ticketId: string }) {
  const [ticket, setTicket] = useState<Awaited<ReturnType<typeof fetchSupportTicket>> | null>(null);
  const [reply, setReply] = useState("");
  const [internal, setInternal] = useState(false);
  const reload = useCallback(() => {
    void fetchSupportTicket(ticketId).then(setTicket).catch(() => setTicket(null));
  }, [ticketId]);
  useEffect(() => {
    reload();
  }, [reload]);
  if (!ticket) return <p className="text-sm text-slate-500">Loading…</p>;
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="lg:col-span-2 space-y-4">
        <AdminCard className="p-4">
          <h2 className="font-semibold">{ticket.subject}</h2>
          <p className="mt-2 text-sm text-slate-600">{ticket.description}</p>
        </AdminCard>
        <div className="space-y-2">
          {ticket.messages.map((m) => (
            <AdminCard key={m.id} className={`p-3 text-sm ${m.is_internal ? "border-amber-200 bg-amber-50" : ""}`}>
              <p className="text-xs text-slate-500">{new Date(m.created_at).toLocaleString()}{m.is_internal ? " · internal" : ""}</p>
              <p className="mt-1 whitespace-pre-wrap">{m.body}</p>
            </AdminCard>
          ))}
        </div>
        <AdminCard className="p-4 space-y-2">
          <textarea className="w-full rounded border p-2 text-sm" rows={3} value={reply} onChange={(e) => setReply(e.target.value)} />
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={internal} onChange={(e) => setInternal(e.target.checked)} />
            Internal note
          </label>
          <button
            type="button"
            className="rounded bg-blue-800 px-3 py-2 text-sm text-white"
            onClick={() => void postSupportTicketMessage(ticketId, { body: reply, is_internal: internal }).then(() => { setReply(""); reload(); })}
          >
            Send
          </button>
        </AdminCard>
      </div>
      <AdminCard className="p-4 space-y-3 text-sm">
        <p><span className="text-slate-500">Status:</span> {ticket.status}</p>
        <p><span className="text-slate-500">Priority:</span> {ticket.priority}</p>
        <select
          className="w-full rounded border px-2 py-1"
          value={ticket.status}
          onChange={(e) => void setSupportTicketStatus(ticketId, e.target.value).then(reload)}
        >
          {["open", "in_progress", "waiting_customer", "resolved", "closed"].map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button
          type="button"
          className="w-full rounded border px-2 py-1"
          onClick={() => {
            const uid = readUserIdFromDocumentCookie();
            if (uid) void assignSupportTicket(ticketId, uid).then(reload);
          }}
        >
          Assign to me
        </button>
      </AdminCard>
    </div>
  );
}

type PartnerRow = Awaited<ReturnType<typeof fetchPartners>>[number];

export function PartnerDetailPanel({ partnerId }: { partnerId: string }) {
  const [tab, setTab] = useState<"overview" | "referrals" | "commissions">("overview");
  const [partner, setPartner] = useState<PartnerRow | null>(null);
  const [referrals, setReferrals] = useState<Awaited<ReturnType<typeof fetchPartnerReferrals>>>([]);
  const [commissions, setCommissions] = useState<Awaited<ReturnType<typeof fetchPartnerCommissions>>>([]);
  useEffect(() => {
    void fetchPartners().then((rows) => setPartner(rows.find((r) => r.id === partnerId) ?? null));
  }, [partnerId]);
  useEffect(() => {
    if (tab === "referrals") void fetchPartnerReferrals(partnerId).then(setReferrals);
    if (tab === "commissions") void fetchPartnerCommissions(partnerId).then(setCommissions);
  }, [tab, partnerId]);
  if (!partner) return <p className="text-sm text-slate-500">Loading…</p>;
  const refLink = `https://app.nextiot.local/signup?ref=${partner.referral_code}`;
  return (
    <div className="space-y-4">
      <div className="flex gap-2 border-b pb-2 text-sm">
        {(["overview", "referrals", "commissions"] as const).map((t) => (
          <button
            key={t}
            type="button"
            className={`px-3 py-1 rounded ${tab === t ? "bg-slate-100 font-medium" : "text-slate-600"}`}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>
      {tab === "overview" ? (
        <AdminCard className="p-4 text-sm space-y-2">
          <p className="text-lg font-semibold">{partner.name}</p>
          <p>Tier: {partner.tier} · Status: {partner.status}</p>
          <p>Commission: {partner.commission_percent}%</p>
          <p>Referral code: <code>{partner.referral_code}</code></p>
          <p className="text-slate-600 break-all">Link: {refLink}</p>
        </AdminCard>
      ) : null}
      {tab === "referrals" ? (
        <AdminDataTable
          rowKey={(r) => r.id}
          rows={referrals}
          columns={[
            { key: "t", header: "Tenant", render: (r) => r.tenant_id },
            { key: "rev", header: "Revenue IDR", render: (r) => r.total_revenue_idr },
          ]}
        />
      ) : null}
      {tab === "commissions" ? (
        <div className="space-y-3">
          <button
            type="button"
            className="rounded bg-blue-800 px-3 py-2 text-sm text-white"
            onClick={() => {
              const month = new Date().toISOString().slice(0, 7) + "-01";
              void calculatePartnerCommission(partnerId, month).then(() =>
                fetchPartnerCommissions(partnerId).then(setCommissions),
              );
            }}
          >
            Calculate this month
          </button>
          <AdminDataTable
            rowKey={(r) => r.id}
            rows={commissions}
            columns={[
              { key: "p", header: "Period", render: (r) => r.period_month },
              { key: "amt", header: "IDR", render: (r) => r.total_commission_idr },
              { key: "st", header: "Status", render: (r) => r.status },
              {
                key: "pay",
                header: "",
                render: (r) =>
                  r.status === "pending" ? (
                    <button
                      type="button"
                      className="text-blue-800"
                      onClick={() => void markPartnerCommissionPaid(partnerId, r.id).then(() =>
                        fetchPartnerCommissions(partnerId).then(setCommissions),
                      )}
                    >
                      Mark paid
                    </button>
                  ) : null,
              },
            ]}
          />
        </div>
      ) : null}
    </div>
  );
}

export function ImpersonationAuditPanel() {
  const [rows, setRows] = useState<Awaited<ReturnType<typeof fetchImpersonationSessions>>>([]);
  useEffect(() => {
    void fetchImpersonationSessions().then(setRows).catch(() => setRows([]));
  }, []);
  return (
    <AdminDataTable
      rowKey={(r) => r.id}
      rows={rows}
      columns={[
        { key: "sa", header: "Super admin", render: (r) => r.super_admin_user_id ?? "—" },
        { key: "tn", header: "Tenant", render: (r) => r.tenant_id ?? "—" },
        { key: "st", header: "Started", render: (r) => new Date(r.started_at).toLocaleString() },
        { key: "dur", header: "Duration (s)", render: (r) => r.duration_seconds ?? "—" },
        { key: "ac", header: "Actions", render: (r) => r.action_count },
      ]}
    />
  );
}
