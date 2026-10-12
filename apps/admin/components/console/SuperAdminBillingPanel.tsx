"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { AdminCard } from "@/components/ui/AdminCard";
import {
  fetchSuperAdminInvoices,
  fetchSuperAdminRevenue,
  formatIdr,
  runBillingCycle,
  type PlatformInvoice,
  type RevenueReport,
} from "@/lib/api/super-admin";

type Tab = "invoices" | "revenue" | "cycle";

export function SuperAdminBillingPanel() {
  const [tab, setTab] = useState<Tab>("invoices");
  const [invoiceStatus, setInvoiceStatus] = useState("");
  const [invoices, setInvoices] = useState<PlatformInvoice[]>([]);
  const [revenue, setRevenue] = useState<RevenueReport | null>(null);
  const [cycleLog, setCycleLog] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (tab === "invoices") {
      void fetchSuperAdminInvoices(invoiceStatus || undefined)
        .then(setInvoices)
        .catch(() => setInvoices([]));
    }
    if (tab === "revenue") {
      void fetchSuperAdminRevenue(12)
        .then(setRevenue)
        .catch(() => setRevenue(null));
    }
  }, [tab, invoiceStatus]);

  const onRunCycle = async () => {
    setBusy(true);
    try {
      const result = await runBillingCycle();
      setCycleLog(
        `Created ${result.invoices_created} invoices; past_due ${result.past_due_marked}; expired ${result.expired_marked}`,
      );
    } catch (e) {
      setCycleLog(e instanceof Error ? e.message : "Billing cycle failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2 border-b border-slate-200">
        {(
          [
            ["invoices", "Invoices"],
            ["revenue", "Revenue"],
            ["cycle", "Billing cycle"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={`border-b-2 px-4 py-2 text-sm font-medium ${
              tab === id ? "border-blue-800 text-blue-800" : "border-transparent text-slate-500"
            }`}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "invoices" ? (
        <>
          <select
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            value={invoiceStatus}
            onChange={(e) => setInvoiceStatus(e.target.value)}
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
          </select>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-100 text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-4 py-3 text-left">Invoice</th>
                  <th className="px-4 py-3 text-left">Total</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-left">Due</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.id} className="border-t border-slate-200">
                    <td className="px-4 py-3">{inv.invoice_number}</td>
                    <td className="px-4 py-3">{formatIdr(inv.total_idr)}</td>
                    <td className="px-4 py-3">{inv.status}</td>
                    <td className="px-4 py-3">{inv.due_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}

      {tab === "revenue" && revenue ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <AdminCard className="p-5">
            <p className="text-xs uppercase text-slate-400">MRR</p>
            <p className="text-2xl font-semibold">{formatIdr(revenue.mrr_idr)}</p>
            <p className="mt-2 text-sm text-slate-500">ARR {formatIdr(revenue.arr_idr)}</p>
            <ul className="mt-4 space-y-1 text-sm">
              {Object.entries(revenue.by_plan).map(([code, amount]) => (
                <li key={code} className="flex justify-between">
                  <span>{code}</span>
                  <span>{formatIdr(amount)}</span>
                </li>
              ))}
            </ul>
          </AdminCard>
          <AdminCard className="h-72 p-5">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={revenue.growth_12m}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip formatter={(v) => formatIdr(Number(v))} />
                <Bar dataKey="revenue_idr" fill="#059669" />
              </BarChart>
            </ResponsiveContainer>
          </AdminCard>
        </div>
      ) : null}

      {tab === "cycle" ? (
        <AdminCard className="space-y-4 p-5">
          <p className="text-sm text-slate-500">Manually run subscription billing cycle (invoices + past_due).</p>
          <button
            type="button"
            disabled={busy}
            className="rounded-lg bg-blue-800 px-4 py-2 text-sm text-white disabled:opacity-50"
            onClick={() => void onRunCycle()}
          >
            Run billing cycle
          </button>
          {cycleLog ? <p className="text-sm text-slate-900">{cycleLog}</p> : null}
        </AdminCard>
      ) : null}
    </div>
  );
}
