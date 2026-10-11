"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { AdminShell } from "@/components/AdminShell";
import { CommandCard } from "@/components/ui/CommandCard";
import { fetchSuperAdminTenantDetail, type TenantDetail } from "@/lib/api/super-admin";

export default function AdminTenantDetailPage() {
  const params = useParams();
  const tenantId = typeof params.id === "string" ? params.id : "";
  const [detail, setDetail] = useState<TenantDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!tenantId) return;
    void fetchSuperAdminTenantDetail(tenantId)
      .then(setDetail)
      .catch(() => setError("Failed to load tenant"));
  }, [tenantId]);

  return (
    <AdminShell title="Tenant detail">
      <Link href="/tenants" className="text-sm text-command-accent hover:underline">
        ← Back to tenants
      </Link>
      {error ? <p className="mt-4 text-sm text-red-400">{error}</p> : null}
      {!detail && !error ? <p className="mt-4 text-sm text-command-secondary">Loading…</p> : null}
      {detail ? (
        <CommandCard className="mt-4 space-y-3 p-6 font-mono text-sm">
          <p>
            <span className="text-command-tertiary">ID</span> {detail.id}
          </p>
          <p>
            <span className="text-command-tertiary">Name</span> {detail.name}
          </p>
          <p>
            <span className="text-command-tertiary">Slug</span> {detail.slug}
          </p>
          <p>
            <span className="text-command-tertiary">Plan</span> {detail.plan_code ?? "—"}
          </p>
          <p>
            <span className="text-command-tertiary">Status</span> {detail.subscription_status ?? "—"}
          </p>
          <p>
            <span className="text-command-tertiary">Devices</span> {detail.device_count}
          </p>
          <p>
            <span className="text-command-tertiary">Users</span> {detail.user_count}
          </p>
          <p>
            <span className="text-command-tertiary">Created</span> {detail.created_at}
          </p>
        </CommandCard>
      ) : null}
    </AdminShell>
  );
}
