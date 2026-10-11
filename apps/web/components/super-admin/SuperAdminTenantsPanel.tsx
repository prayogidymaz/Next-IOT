"use client";

import { useCallback, useEffect, useState } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import {
  changeTenantPlan,
  extendTenantTrial,
  fetchSuperAdminTenantDetail,
  fetchSuperAdminTenants,
  suspendTenant,
  unsuspendTenant,
  type TenantAdminItem,
  type TenantDetail,
} from "@/lib/api/super-admin";

export function SuperAdminTenantsPanel() {
  const [rows, setRows] = useState<TenantAdminItem[]>([]);
  const [status, setStatus] = useState("");
  const [plan, setPlan] = useState("");
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState<TenantDetail | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const data = await fetchSuperAdminTenants({
      status: status || undefined,
      plan: plan || undefined,
      q: q || undefined,
    });
    setRows(data);
  }, [status, plan, q]);

  useEffect(() => {
    void refresh().catch(() => setRows([]));
  }, [refresh]);

  const openDetail = async (id: string) => {
    setBusy(true);
    try {
      setSelected(await fetchSuperAdminTenantDetail(id));
    } catch {
      setError("Failed to load tenant detail");
    } finally {
      setBusy(false);
    }
  };

  const runAction = async (fn: () => Promise<void>) => {
    if (!selected) return;
    setBusy(true);
    setError(null);
    try {
      await fn();
      await refresh();
      setSelected(await fetchSuperAdminTenantDetail(selected.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Action failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <CreamCard className="flex flex-wrap gap-3 p-4">
        <input
          className="min-w-[200px] flex-1 rounded-lg border border-cream-border px-3 py-2 text-sm"
          placeholder="Search name or slug"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <select className="rounded-lg border border-cream-border px-3 py-2 text-sm" value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All status</option>
          <option value="active">Active</option>
          <option value="trial">Trial</option>
          <option value="suspended">Suspended</option>
        </select>
        <select className="rounded-lg border border-cream-border px-3 py-2 text-sm" value={plan} onChange={(e) => setPlan(e.target.value)}>
          <option value="">All plans</option>
          <option value="free">Free</option>
          <option value="starter">Starter</option>
          <option value="pro">Pro</option>
          <option value="enterprise">Enterprise</option>
        </select>
        <button type="button" className="rounded-lg bg-accent-cobalt px-4 py-2 text-sm text-white" onClick={() => void refresh()}>
          Apply
        </button>
      </CreamCard>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <div className="overflow-x-auto rounded-xl border border-cream-border bg-white">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-cream-border bg-cream-alt text-xs uppercase text-ink-tertiary">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Slug</th>
              <th className="px-4 py-3">Plan</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Devices</th>
              <th className="px-4 py-3">Users</th>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b border-cream-border hover:bg-cream-alt/50">
                <td className="px-4 py-3 font-medium">{row.name}</td>
                <td className="px-4 py-3 text-ink-secondary">{row.slug}</td>
                <td className="px-4 py-3">{row.plan_code ?? "—"}</td>
                <td className="px-4 py-3">{row.is_active ? row.subscription_status ?? "—" : "suspended"}</td>
                <td className="px-4 py-3">{row.device_count}</td>
                <td className="px-4 py-3">{row.user_count}</td>
                <td className="px-4 py-3 text-ink-secondary">{new Date(row.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3">
                  <button type="button" className="text-accent-cobalt hover:underline" onClick={() => void openDetail(row.id)}>
                    Manage
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected ? (
        <CreamCard className="space-y-4 p-5">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <h3 className="text-lg font-semibold">{selected.name}</h3>
              <p className="text-sm text-ink-secondary">{selected.slug}</p>
            </div>
            <button type="button" className="text-sm text-ink-secondary" onClick={() => setSelected(null)}>
              Close
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {selected.is_active ? (
              <button
                type="button"
                disabled={busy}
                className="rounded-lg border border-red-200 px-3 py-1.5 text-sm text-red-700"
                onClick={() => void runAction(() => suspendTenant(selected.id, "HQ manual suspend"))}
              >
                Suspend
              </button>
            ) : (
              <button
                type="button"
                disabled={busy}
                className="rounded-lg border border-cream-border px-3 py-1.5 text-sm"
                onClick={() => void runAction(() => unsuspendTenant(selected.id))}
              >
                Unsuspend
              </button>
            )}
            {[7, 14, 30].map((days) => (
              <button
                key={days}
                type="button"
                disabled={busy}
                className="rounded-lg border border-cream-border px-3 py-1.5 text-sm"
                onClick={() => void runAction(() => extendTenantTrial(selected.id, days))}
              >
                Trial +{days}d
              </button>
            ))}
            {(["starter", "pro", "enterprise"] as const).map((code) => (
              <button
                key={code}
                type="button"
                disabled={busy}
                className="rounded-lg bg-cream-muted px-3 py-1.5 text-sm"
                onClick={() => void runAction(() => changeTenantPlan(selected.id, code, true))}
              >
                Plan {code}
              </button>
            ))}
          </div>
          <details className="rounded-lg border border-cream-border p-3">
            <summary className="cursor-pointer text-sm font-medium">Audit log</summary>
            <ul className="mt-3 space-y-2 text-xs text-ink-secondary">
              {selected.audit_entries.length === 0 ? (
                <li>No super-admin actions recorded</li>
              ) : (
                selected.audit_entries.map((a) => (
                  <li key={a.id}>
                    {a.action} — {new Date(a.created_at).toLocaleString()}
                  </li>
                ))
              )}
            </ul>
          </details>
        </CreamCard>
      ) : null}
    </div>
  );
}
