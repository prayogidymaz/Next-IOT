"use client";

import { useCallback, useEffect, useState } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import {
  listFirmwareReleases,
  listReleaseRollouts,
  publishFirmwareRelease,
  uploadFirmwareRelease,
  type FirmwareRelease,
  type OtaRollout,
} from "@/lib/api/firmware-releases";

export function FirmwareReleasesPanel() {
  const [releases, setReleases] = useState<FirmwareRelease[]>([]);
  const [version, setVersion] = useState("1.0.0");
  const [category, setCategory] = useState("SENSOR");
  const [file, setFile] = useState<File | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [rollouts, setRollouts] = useState<OtaRollout[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const rows = await listFirmwareReleases();
    setReleases(rows);
  }, []);

  useEffect(() => {
    void refresh().catch(() => setReleases([]));
  }, [refresh]);

  const onUpload = async () => {
    if (!file) {
      setError("Pilih file firmware (.bin)");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await uploadFirmwareRelease({ file, version, targetDeviceCategory: category });
      setFile(null);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload gagal");
    } finally {
      setBusy(false);
    }
  };

  const onPublish = async (releaseId: string) => {
    setBusy(true);
    setError(null);
    try {
      const result = await publishFirmwareRelease(releaseId);
      await refresh();
      setExpandedId(releaseId);
      alert(`Rollout: ${result.rollouts_created} baru, ${result.targeted_devices} device`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Publish gagal");
    } finally {
      setBusy(false);
    }
  };

  const onExpandRollouts = async (releaseId: string) => {
    if (expandedId === releaseId) {
      setExpandedId(null);
      return;
    }
    setExpandedId(releaseId);
    try {
      const rows = await listReleaseRollouts(releaseId);
      setRollouts(rows);
    } catch {
      setRollouts([]);
    }
  };

  return (
    <div className="space-y-6">
      <CreamCard title="Upload release">
        <div className="grid gap-3 md:grid-cols-3">
          <label className="text-sm">
            Version
            <input
              className="mt-1 w-full rounded border border-cream-border px-2 py-1"
              value={version}
              onChange={(e) => setVersion(e.target.value)}
            />
          </label>
          <label className="text-sm">
            Device category
            <input
              className="mt-1 w-full rounded border border-cream-border px-2 py-1"
              value={category}
              onChange={(e) => setCategory(e.target.value.toUpperCase())}
            />
          </label>
          <label className="text-sm">
            Firmware file
            <input
              type="file"
              className="mt-1 block w-full text-sm"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>
        </div>
        <button
          type="button"
          disabled={busy}
          className="mt-4 rounded bg-accent-violet px-4 py-2 text-sm text-white disabled:opacity-50"
          onClick={() => void onUpload()}
        >
          Upload
        </button>
      </CreamCard>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <CreamCard title="Releases">
        <ul className="divide-y divide-cream-border">
          {releases.map((r) => (
            <li key={r.id} className="py-3 text-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="font-medium">{r.version}</span>
                  <span className="ml-2 text-ink-secondary">{r.target_device_category}</span>
                  <span className="ml-2 rounded bg-cream-muted px-2 py-0.5 text-xs">{r.status}</span>
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    disabled={busy}
                    className="rounded border border-cream-border px-3 py-1 text-xs"
                    onClick={() => void onPublish(r.id)}
                  >
                    Rollout (MQTT)
                  </button>
                  <button
                    type="button"
                    className="rounded border border-cream-border px-3 py-1 text-xs"
                    onClick={() => void onExpandRollouts(r.id)}
                  >
                    {expandedId === r.id ? "Hide" : "Rollouts"}
                  </button>
                </div>
              </div>
              {expandedId === r.id ? (
                <ul className="mt-2 space-y-1 pl-2 text-xs text-ink-secondary">
                  {rollouts.length === 0 ? (
                    <li>No rollouts yet</li>
                  ) : (
                    rollouts.map((o) => (
                      <li key={o.id}>
                        {o.device_name}: {o.status}
                      </li>
                    ))
                  )}
                </ul>
              ) : null}
            </li>
          ))}
          {releases.length === 0 ? <li className="py-4 text-ink-secondary">Belum ada release</li> : null}
        </ul>
      </CreamCard>
    </div>
  );
}
