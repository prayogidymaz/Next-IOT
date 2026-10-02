"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import {
  ProfileDomainBadge,
  ProfileStatusBadge,
  PROFILE_DOMAINS,
} from "@/components/device-profiles/profile-badges";
import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";
import { useHqToast } from "@/hooks/useHqToast";
import { useHqUser } from "@/hooks/useHqUser";
import { listDeviceProfiles } from "@/lib/api/deviceProfiles";
import type { DeviceProfile, ProfileDomain, ProfileStatus } from "@/lib/api/device-profiles-schemas";
import { RBAC_DENIED_MESSAGE } from "@/lib/hq/rbac";

export function DeviceProfilesListPage() {
  const router = useRouter();
  const { canWriteProfiles } = useHqUser();
  const { showToast } = useHqToast();
  const [rows, setRows] = useState<DeviceProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [domain, setDomain] = useState<ProfileDomain | "">("");
  const [status, setStatus] = useState<ProfileStatus | "">("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listDeviceProfiles({
        domain: domain || undefined,
        status: status || undefined,
      });
      setRows(data);
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal memuat profil", "error");
    } finally {
      setLoading(false);
    }
  }, [domain, status, showToast]);

  useEffect(() => {
    void load();
  }, [load]);

  function onNewClick() {
    if (!canWriteProfiles) {
      showToast(RBAC_DENIED_MESSAGE, "error");
      return;
    }
    router.push("/device-profiles/new");
  }

  return (
    <HqPageContent description="Thing model per tenant — telemetry, attributes, dan commands dengan versioning.">
      <CreamCard className="p-4">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div className="flex flex-wrap gap-3">
            <label className="text-xs text-ink-secondary">
              Domain
              <select
                value={domain}
                onChange={(e) => setDomain(e.target.value as ProfileDomain | "")}
                className="mt-1 block rounded-xl border border-cream-border bg-white px-3 py-2 text-sm"
              >
                <option value="">Semua</option>
                {PROFILE_DOMAINS.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-xs text-ink-secondary">
              Status
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as ProfileStatus | "")}
                className="mt-1 block rounded-xl border border-cream-border bg-white px-3 py-2 text-sm"
              >
                <option value="">Semua</option>
                <option value="draft">draft</option>
                <option value="published">published</option>
                <option value="archived">archived</option>
              </select>
            </label>
          </div>
          <button
            type="button"
            onClick={onNewClick}
            className="rounded-xl bg-accent-emerald px-4 py-2 text-sm font-semibold text-white shadow-sm hover:opacity-90"
          >
            New Profile
          </button>
        </div>
      </CreamCard>

      <CreamCard className="overflow-x-auto p-0">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-cream-border bg-cream-alt text-xs uppercase text-ink-tertiary">
            <tr>
              <th className="px-4 py-3">Key</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Domain</th>
              <th className="px-4 py-3">Ver</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Updated</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-ink-secondary">
                  Memuat…
                </td>
              </tr>
            ) : null}
            {!loading && rows.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-ink-secondary">
                  Belum ada profil.
                </td>
              </tr>
            ) : null}
            {rows.map((row) => (
              <tr
                key={row.id}
                className="cursor-pointer border-b border-cream-border hover:bg-cream-muted/60"
                onClick={() => router.push(`/device-profiles/${row.id}`)}
              >
                <td className="px-4 py-3 font-mono text-xs">{row.key}</td>
                <td className="px-4 py-3 font-medium text-ink-primary">{row.name}</td>
                <td className="px-4 py-3">
                  <ProfileDomainBadge domain={row.domain} />
                </td>
                <td className="px-4 py-3">{row.version}</td>
                <td className="px-4 py-3">
                  <ProfileStatusBadge status={row.status} />
                </td>
                <td className="px-4 py-3 text-xs text-ink-secondary">
                  {new Date(row.updated_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CreamCard>
      <p className="text-xs text-ink-tertiary">
        Butuh assign ke perangkat? Buka{" "}
        <Link href="/devices" className="text-accent-cobalt underline">
          daftar perangkat
        </Link>
        .
      </p>
    </HqPageContent>
  );
}
