"use client";

import { useCallback, useEffect, useState } from "react";

import { ClaimTokensTable, useClaimCountdownTick } from "@/components/claim-tokens/claim-tokens-table";
import { GenerateClaimModal } from "@/components/claim-tokens/generate-claim-modal";
import { QrDisplayModal } from "@/components/claim-tokens/qr-display-modal";
import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";
import { useHqToast } from "@/hooks/useHqToast";
import { useHqUser } from "@/hooks/useHqUser";
import type { ClaimToken } from "@/lib/api/claim-tokens-schemas";
import { listClaimTokens, revokeClaimToken } from "@/lib/api/claimTokens";

export function ClaimTokensPage() {
  const { canAdminClaimTokens } = useHqUser();
  const { showToast } = useHqToast();
  const [rows, setRows] = useState<ClaimToken[]>([]);
  const [loading, setLoading] = useState(true);
  const [generateOpen, setGenerateOpen] = useState(false);
  const [qrToken, setQrToken] = useState<ClaimToken | null>(null);
  const now = useClaimCountdownTick(10_000);

  const reload = useCallback(async () => {
    try {
      setRows(await listClaimTokens());
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal memuat claim tokens", "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    void reload();
  }, [reload]);

  async function onRevoke(row: ClaimToken) {
    if (!canAdminClaimTokens) return;
    if (!window.confirm(`Revoke claim token untuk "${row.device_name}"?`)) return;
    try {
      await revokeClaimToken(row.id);
      await reload();
      showToast("Token di-revoke.", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal revoke", "error");
    }
  }

  return (
    <HqPageContent description="QR claim tokens untuk onboarding perangkat mobile.">
      <div className="mb-4 flex justify-end">
        {canAdminClaimTokens ? (
          <button
            type="button"
            className="rounded-lg bg-accent-cobalt px-4 py-2 text-sm text-white"
            onClick={() => setGenerateOpen(true)}
          >
            + Generate Claim Token
          </button>
        ) : null}
      </div>
      <CreamCard className="overflow-x-auto p-0">
        {loading ? (
          <p className="px-4 py-6 text-sm text-ink-secondary">Memuat…</p>
        ) : rows.length === 0 ? (
          <p className="px-4 py-6 text-sm text-ink-secondary">Belum ada claim token.</p>
        ) : (
          <ClaimTokensTable
            rows={rows}
            now={now}
            canAdmin={canAdminClaimTokens}
            onViewQr={setQrToken}
            onRevoke={(row) => void onRevoke(row)}
          />
        )}
      </CreamCard>
      <GenerateClaimModal
        open={generateOpen}
        onClose={() => setGenerateOpen(false)}
        onCreated={(token) => {
          setQrToken(token);
          void reload();
        }}
      />
      {qrToken ? <QrDisplayModal token={qrToken} open onClose={() => setQrToken(null)} /> : null}
    </HqPageContent>
  );
}
