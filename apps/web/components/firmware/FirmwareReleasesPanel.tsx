"use client";

import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { useHqToast } from "@/hooks/useHqToast";
import {
  listFirmwareReleases,
  listReleaseRollouts,
  publishFirmwareRelease,
  uploadFirmwareRelease,
  type FirmwareRelease,
  type OtaRollout,
} from "@/lib/api/firmware-releases";
import { Card, CardContent, CardHeader, CardTitle } from "@/src/components/ui/card";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { Input } from "@/src/components/ui/input";
import { Label } from "@/src/components/ui/label";

export function FirmwareReleasesPanel() {
  const { showToast } = useHqToast();
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
      showToast(`Rollout: ${result.rollouts_created} baru, ${result.targeted_devices} device`, "success");
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
      <Card>
        <CardHeader>
          <CardTitle>Upload release</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="fw-version">Version</Label>
              <Input id="fw-version" value={version} onChange={(e) => setVersion(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="fw-category">Device category</Label>
              <Input id="fw-category" value={category} onChange={(e) => setCategory(e.target.value.toUpperCase())} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="fw-file">Firmware file</Label>
              <Input id="fw-file" type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
            </div>
          </div>
          <Button disabled={busy} onClick={() => void onUpload()}>
            Upload
          </Button>
        </CardContent>
      </Card>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <Card>
        <CardHeader>
          <CardTitle>Releases</CardTitle>
        </CardHeader>
        <CardContent>
          {releases.length === 0 ? (
            <EmptyState title="Belum ada release" description="Upload firmware baru untuk mulai" />
          ) : (
            <ul className="divide-y divide-border">
              {releases.map((r) => (
                <li key={r.id} className="py-3 text-sm">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <span className="font-medium text-foreground">{r.version}</span>
                      <span className="ml-2 text-muted-foreground">{r.target_device_category}</span>
                      <span className="ml-2 rounded bg-muted px-2 py-0.5 text-xs">{r.status}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" disabled={busy} onClick={() => void onPublish(r.id)}>
                        Rollout (MQTT)
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => void onExpandRollouts(r.id)}>
                        {expandedId === r.id ? "Hide" : "Rollouts"}
                      </Button>
                    </div>
                  </div>
                  {expandedId === r.id ? (
                    <ul className="mt-2 space-y-1 pl-2 text-xs text-muted-foreground">
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
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
