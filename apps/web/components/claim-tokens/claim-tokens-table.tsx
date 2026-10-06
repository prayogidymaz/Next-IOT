"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import type { ClaimToken } from "@/lib/api/claim-tokens-schemas";

function tokenStatus(row: ClaimToken, now: number): "claimed" | "expired" | "pending" {
  if (row.claimed_at) return "claimed";
  if (new Date(row.expires_at).getTime() <= now) return "expired";
  return "pending";
}

function expiresLabel(row: ClaimToken, now: number): string {
  if (row.claimed_at) return "—";
  const ms = new Date(row.expires_at).getTime() - now;
  if (ms <= 0) return "Expired";
  const hours = Math.floor(ms / 3_600_000);
  if (hours >= 1) return `${hours} jam lagi`;
  const mins = Math.max(1, Math.floor(ms / 60_000));
  return `${mins} menit lagi`;
}

type ClaimTokensTableProps = {
  rows: ClaimToken[];
  now: number;
  canAdmin: boolean;
  onViewQr: (row: ClaimToken) => void;
  onRevoke: (row: ClaimToken) => void;
};

export function ClaimTokensTable({ rows, now, canAdmin, onViewQr, onRevoke }: ClaimTokensTableProps) {
  return (
    <table className="min-w-full text-sm">
      <thead className="border-b border-cream-border bg-cream-alt text-xs uppercase text-ink-tertiary">
        <tr>
          <th className="px-4 py-3 text-left">Nama Device</th>
          <th className="px-4 py-3 text-left">Type</th>
          <th className="px-4 py-3 text-left">Expires</th>
          <th className="px-4 py-3 text-left">Status</th>
          <th className="px-4 py-3 text-left">Created By</th>
          <th className="px-4 py-3 text-left">Actions</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => {
          const status = tokenStatus(row, now);
          const muted = status === "expired";
          return (
            <tr key={row.id} className={`border-b border-cream-border ${muted ? "text-ink-tertiary" : ""}`}>
              <td className="px-4 py-3 font-medium">{row.device_name}</td>
              <td className="px-4 py-3">{row.device_type}</td>
              <td className="px-4 py-3">{expiresLabel(row, now)}</td>
              <td className="px-4 py-3">
                {status === "claimed" ? (
                  <span className="rounded-full bg-accent-emerald-soft px-2 py-0.5 text-xs text-accent-emerald">
                    Claimed
                    {row.claimed_device_id ? (
                      <>
                        {" "}
                        <Link href={`/devices/${row.claimed_device_id}`} className="underline">
                          device
                        </Link>
                      </>
                    ) : null}
                  </span>
                ) : null}
                {status === "pending" ? (
                  <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-800">Pending</span>
                ) : null}
                {status === "expired" ? (
                  <span className="rounded-full bg-cream-muted px-2 py-0.5 text-xs">Expired</span>
                ) : null}
              </td>
              <td className="px-4 py-3 font-mono text-xs">
                {row.created_by_user_id ? row.created_by_user_id.slice(0, 8) : "—"}
              </td>
              <td className="px-4 py-3 space-x-2">
                <button type="button" className="text-accent-cobalt underline" onClick={() => onViewQr(row)}>
                  View QR
                </button>
                {canAdmin && status === "pending" ? (
                  <button type="button" className="text-red-600 underline" onClick={() => onRevoke(row)}>
                    Revoke
                  </button>
                ) : null}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export function useClaimCountdownTick(intervalMs = 10_000): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), intervalMs);
    return () => window.clearInterval(id);
  }, [intervalMs]);
  return now;
}
