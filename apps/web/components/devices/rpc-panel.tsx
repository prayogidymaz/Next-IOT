"use client";

import { useCallback, useEffect, useState } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import type { DeviceRpcItem } from "@/lib/api/device-rpc-schemas";
import { listDeviceRpc, sendDeviceRpc } from "@/lib/api/device-rpc";
import type { DeviceResponse } from "@/lib/api/devices-schemas";
import { useHqToast } from "@/hooks/useHqToast";
import { useHqUser } from "@/hooks/useHqUser";

type RpcPanelProps = {
  device: DeviceResponse;
};

function statusBadge(status: string): string {
  if (status === "completed") return "bg-green-100 text-green-800";
  if (status === "timeout") return "bg-amber-100 text-amber-900";
  if (status === "failed") return "bg-red-100 text-red-800";
  return "bg-slate-100 text-slate-800";
}

export function RpcPanel({ device }: RpcPanelProps) {
  const { showToast } = useHqToast();
  const { canManageMqttCredentials } = useHqUser();
  const [method, setMethod] = useState("reboot");
  const [paramsJson, setParamsJson] = useState("{}");
  const [timeoutSec, setTimeoutSec] = useState(30);
  const [lastResult, setLastResult] = useState<string>("");
  const [history, setHistory] = useState<DeviceRpcItem[]>([]);
  const [sending, setSending] = useState(false);

  const reloadHistory = useCallback(async () => {
    try {
      const items = await listDeviceRpc(device.id);
      setHistory(items.slice(0, 10));
    } catch {
      /* ignore polling errors */
    }
  }, [device.id]);

  useEffect(() => {
    void reloadHistory();
  }, [reloadHistory]);

  async function send() {
    if (!canManageMqttCredentials) return;
    setSending(true);
    setLastResult("pending…");
    try {
      const params = JSON.parse(paramsJson) as Record<string, unknown>;
      const { status, body } = await sendDeviceRpc(device.id, {
        method,
        params,
        timeout_seconds: timeoutSec,
      });
      setLastResult(`${status}: ${JSON.stringify(body)}`);
      await reloadHistory();
      if (status >= 400) {
        showToast(`RPC: ${body.status}`, "error");
      } else {
        showToast(`RPC: ${body.status}`, "success");
      }
    } catch (err) {
      setLastResult(err instanceof Error ? err.message : "Gagal");
      showToast("Gagal mengirim RPC", "error");
    } finally {
      setSending(false);
    }
  }

  return (
    <CreamCard className="mt-4 p-5">
      <h2 className="text-lg font-semibold text-ink-primary">Remote Command (RPC)</h2>
      {canManageMqttCredentials ? (
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <div>
            <label className="text-xs text-ink-secondary">Method</label>
            <input
              className="mt-1 w-full rounded border px-2 py-1 text-sm"
              value={method}
              onChange={(e) => setMethod(e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs text-ink-secondary">Timeout (s)</label>
            <input
              type="number"
              min={1}
              max={300}
              className="mt-1 w-full rounded border px-2 py-1 text-sm"
              value={timeoutSec}
              onChange={(e) => setTimeoutSec(Number(e.target.value))}
            />
          </div>
          <div className="md:col-span-2">
            <label className="text-xs text-ink-secondary">Params (JSON)</label>
            <textarea
              className="mt-1 w-full rounded border px-2 py-1 font-mono text-xs"
              rows={4}
              value={paramsJson}
              onChange={(e) => setParamsJson(e.target.value)}
            />
          </div>
          <button
            type="button"
            disabled={sending}
            className="rounded bg-ink-primary px-4 py-2 text-sm text-white disabled:opacity-50"
            onClick={() => void send()}
          >
            {sending ? "Sending…" : "Send Command"}
          </button>
        </div>
      ) : (
        <p className="mt-2 text-sm text-ink-secondary">Operator+ diperlukan untuk mengirim RPC.</p>
      )}
      {lastResult ? (
        <pre className="mt-4 overflow-x-auto rounded bg-cream-muted p-2 text-xs">{lastResult}</pre>
      ) : null}
      <h3 className="mt-6 text-sm font-semibold">History (10 terakhir)</h3>
      <ul className="mt-2 space-y-2 text-sm">
        {history.map((row) => (
          <li key={row.id} className="flex flex-wrap items-center gap-2 border-b border-cream-border/60 pb-2">
            <span className={`rounded px-2 py-0.5 text-xs ${statusBadge(row.status)}`}>{row.status}</span>
            <span className="font-mono text-xs">{row.method}</span>
            <span className="text-xs text-ink-secondary">{new Date(row.requested_at).toLocaleString()}</span>
          </li>
        ))}
      </ul>
    </CreamCard>
  );
}
