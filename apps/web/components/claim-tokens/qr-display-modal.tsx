"use client";

import { QRCodeCanvas } from "qrcode.react";
import { useRef } from "react";

import type { ClaimToken } from "@/lib/api/claim-tokens-schemas";
import { claimQrPayload } from "@/lib/api/claimTokens";

type QrDisplayModalProps = {
  token: ClaimToken;
  open: boolean;
  onClose: () => void;
};

export function QrDisplayModal({ token, open, onClose }: QrDisplayModalProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  if (!open) return null;
  const qrValue = claimQrPayload(token.qr_code_url, token.claim_token);

  function downloadPng() {
    const canvas = canvasRef.current?.querySelector("canvas");
    if (!canvas) return;
    const url = canvas.toDataURL("image/png");
    const a = document.createElement("a");
    a.href = url;
    a.download = `claim-${token.claim_token.slice(0, 8)}.png`;
    a.click();
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 print:bg-white">
      <div className="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-2xl bg-white p-6 shadow-card print:shadow-none">
        <h3 className="text-lg font-semibold text-ink-primary">Claim QR — {token.device_name}</h3>
        <div ref={canvasRef} className="mt-4 flex justify-center print:mt-8">
          <QRCodeCanvas value={qrValue} size={220} level="M" />
        </div>
        <p className="mt-4 font-mono text-xs break-all text-center">{token.claim_token}</p>
        <p className="mt-2 text-sm text-ink-secondary text-center">
          Buka Next-IOT Mobile App → Add Device → Scan QR
        </p>
        <p className="mt-1 text-xs text-ink-tertiary text-center">
          Expires: {new Date(token.expires_at).toLocaleString()}
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-2 print:hidden">
          <button
            type="button"
            className="rounded-lg bg-accent-cobalt px-4 py-2 text-sm text-white"
            onClick={() => void navigator.clipboard.writeText(token.claim_token)}
          >
            Copy token
          </button>
          <button type="button" className="rounded-lg border border-cream-border px-4 py-2 text-sm" onClick={downloadPng}>
            Download QR PNG
          </button>
          <button type="button" className="rounded-lg border border-cream-border px-4 py-2 text-sm" onClick={() => window.print()}>
            Print QR
          </button>
          <button type="button" className="rounded-lg border border-cream-border px-4 py-2 text-sm" onClick={onClose}>
            Tutup
          </button>
        </div>
      </div>
    </div>
  );
}
