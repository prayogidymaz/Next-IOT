"use client";

import { useCallback, useEffect, useState } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import { useHqToast } from "@/hooks/useHqToast";
import { useHqUser } from "@/hooks/useHqUser";
import type { DeviceCredentialCreate, DeviceCredentialPublic } from "@/lib/api/mqtt-credentials-schemas";
import {
  generateDeviceCredential,
  getDeviceCredential,
  mqttBrokerUrl,
  revokeDeviceCredential,
  rotateDeviceCredential,
} from "@/lib/api/mqttCredentials";
import type { DeviceResponse } from "@/lib/api/devices-schemas";

type MqttCredentialsPanelProps = {
  device: DeviceResponse;
};

function formatRelative(iso: string | null): string {
  if (!iso) return "Belum pernah connect";
  const then = new Date(iso).getTime();
  const diffSec = Math.round((Date.now() - then) / 1000);
  if (diffSec < 60) return `${diffSec} detik lalu`;
  const diffMin = Math.round(diffSec / 60);
  if (diffMin < 60) return `${diffMin} menit lalu`;
  const diffHour = Math.round(diffMin / 60);
  if (diffHour < 48) return `${diffHour} jam lalu`;
  return new Date(iso).toLocaleString();
}

function buildEnvFile(params: {
  broker: string;
  clientId: string;
  accessToken: string;
  tenantId: string;
  deviceId: string;
}): string {
  return [
    `MQTT_BROKER_URL=${params.broker}`,
    `MQTT_CLIENT_ID=${params.clientId}`,
    `MQTT_USERNAME=${params.accessToken}`,
    `MQTT_PASSWORD=${params.accessToken}`,
    `MQTT_TOPIC_PUBLISH=tenants/${params.tenantId}/devices/${params.deviceId}/telemetry`,
    `MQTT_TOPIC_SUBSCRIBE=tenants/${params.tenantId}/devices/${params.deviceId}/commands/+`,
  ].join("\n");
}

type TokenModalProps = {
  open: boolean;
  onClose: () => void;
  created: DeviceCredentialCreate;
  device: DeviceResponse;
};

function TokenModal({ open, onClose, created, device }: TokenModalProps) {
  if (!open) return null;
  const broker = mqttBrokerUrl();
  const pubTopic = `tenants/${device.tenant_id}/devices/${device.id}/telemetry`;
  const subTopic = `tenants/${device.tenant_id}/devices/${device.id}/commands/+`;

  async function copyToken() {
    await navigator.clipboard.writeText(created.access_token);
  }

  function downloadEnv() {
    const blob = new Blob(
      [
        buildEnvFile({
          broker,
          clientId: created.client_id,
          accessToken: created.access_token,
          tenantId: device.tenant_id,
          deviceId: device.id,
        }),
      ],
      { type: "text/plain" },
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `device-${device.id.slice(0, 8)}-mqtt.env`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-white p-6 shadow-card">
        <h3 className="text-lg font-semibold text-ink-primary">MQTT Credential</h3>
        <p className="mt-2 text-sm text-amber-800">
          ⚠️ Token ini hanya muncul SEKALI. Simpan sekarang, tidak bisa dilihat lagi.
        </p>
        <p className="mt-4 font-mono text-xs break-all rounded-lg bg-cream-muted p-3">{created.access_token}</p>
        <dl className="mt-4 space-y-2 text-sm text-ink-secondary">
          <div>
            <dt className="font-medium text-ink-primary">Broker</dt>
            <dd className="font-mono text-xs">{broker}</dd>
          </div>
          <div>
            <dt className="font-medium text-ink-primary">Client ID</dt>
            <dd className="font-mono text-xs">{created.client_id}</dd>
          </div>
          <div>
            <dt className="font-medium text-ink-primary">Username / Password</dt>
            <dd className="font-mono text-xs">access_token (sama)</dd>
          </div>
          <div>
            <dt className="font-medium text-ink-primary">Publish</dt>
            <dd className="font-mono text-xs">{pubTopic}</dd>
          </div>
          <div>
            <dt className="font-medium text-ink-primary">Subscribe</dt>
            <dd className="font-mono text-xs">{subTopic}</dd>
          </div>
        </dl>
        <div className="mt-6 flex flex-wrap gap-2">
          <button type="button" className="rounded-lg bg-accent-cobalt px-4 py-2 text-sm text-white" onClick={() => void copyToken()}>
            Copy token
          </button>
          <button type="button" className="rounded-lg border border-cream-border px-4 py-2 text-sm" onClick={downloadEnv}>
            Download .env
          </button>
          <button type="button" className="rounded-lg border border-cream-border px-4 py-2 text-sm" onClick={onClose}>
            Tutup
          </button>
        </div>
      </div>
    </div>
  );
}

export function MqttCredentialsPanel({ device }: MqttCredentialsPanelProps) {
  const { canManageMqttCredentials } = useHqUser();
  const { showToast } = useHqToast();
  const [credential, setCredential] = useState<DeviceCredentialPublic | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [modal, setModal] = useState<DeviceCredentialCreate | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      setCredential(await getDeviceCredential(device.id));
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal memuat credential", "error");
    } finally {
      setLoading(false);
    }
  }, [device.id, showToast]);

  useEffect(() => {
    void reload();
  }, [reload]);

  async function onGenerate() {
    if (!canManageMqttCredentials) return;
    setBusy(true);
    try {
      const created = await generateDeviceCredential(device.id);
      setModal(created);
      await reload();
      showToast("Credential dibuat.", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal generate", "error");
    } finally {
      setBusy(false);
    }
  }

  async function onRotate() {
    if (!canManageMqttCredentials) return;
    const ok = window.confirm(
      "Rotate akan NON-AKTIFKAN credential lama. Device yang masih pakai token lama akan DISCONNECT. Lanjutkan?",
    );
    if (!ok) return;
    setBusy(true);
    try {
      const created = await rotateDeviceCredential(device.id);
      setModal(created);
      await reload();
      showToast("Credential di-rotate.", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal rotate", "error");
    } finally {
      setBusy(false);
    }
  }

  async function onRevoke() {
    if (!canManageMqttCredentials) return;
    const ok = window.confirm(
      "Revoke permanen non-aktifkan credential. Device tidak bisa connect sampai di-generate ulang. Lanjutkan?",
    );
    if (!ok) return;
    setBusy(true);
    try {
      await revokeDeviceCredential(device.id);
      await reload();
      showToast("Credential di-revoke.", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal revoke", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <CreamCard className="p-5">
        <h2 className="text-lg font-semibold text-ink-primary">MQTT Credentials</h2>
        {loading ? (
          <p className="mt-2 text-sm text-ink-secondary">Memuat…</p>
        ) : credential ? (
          <div className="mt-3 space-y-2 text-sm text-ink-secondary">
            <p>
              Client ID: <span className="font-mono text-ink-primary">{credential.client_id}</span>
            </p>
            <p>
              Status:{" "}
              <span
                className={
                  credential.is_active
                    ? "rounded-full bg-accent-emerald-soft px-2 py-0.5 text-xs text-accent-emerald"
                    : "rounded-full bg-cream-muted px-2 py-0.5 text-xs"
                }
              >
                {credential.is_active ? "Aktif" : "Tidak Aktif"}
              </span>
            </p>
            <p>Last connected: {formatRelative(credential.last_connected_at)}</p>
            <p>Created: {new Date(credential.created_at).toLocaleString()}</p>
            {credential.rotated_at ? <p>Rotated: {new Date(credential.rotated_at).toLocaleString()}</p> : null}
          </div>
        ) : (
          <p className="mt-2 text-sm text-ink-secondary">Belum ada credential MQTT untuk perangkat ini.</p>
        )}
        {canManageMqttCredentials ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {!credential ? (
              <button
                type="button"
                disabled={busy}
                className="rounded-lg bg-accent-cobalt px-4 py-2 text-sm text-white disabled:opacity-50"
                onClick={() => void onGenerate()}
              >
                Generate Credential
              </button>
            ) : null}
            {credential?.is_active ? (
              <>
                <button
                  type="button"
                  disabled={busy}
                  className="rounded-lg border border-cream-border px-4 py-2 text-sm disabled:opacity-50"
                  onClick={() => void onRotate()}
                >
                  Rotate
                </button>
                <button
                  type="button"
                  disabled={busy}
                  className="rounded-lg border border-red-200 px-4 py-2 text-sm text-red-700 disabled:opacity-50"
                  onClick={() => void onRevoke()}
                >
                  Revoke
                </button>
              </>
            ) : null}
          </div>
        ) : (
          <p className="mt-3 text-xs text-ink-tertiary">Hanya operator/admin yang dapat mengelola credential.</p>
        )}
      </CreamCard>
      {modal ? (
        <TokenModal open device={device} created={modal} onClose={() => setModal(null)} />
      ) : null}
    </>
  );
}
