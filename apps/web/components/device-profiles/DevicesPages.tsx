"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { DeviceProfileAssignPanel } from "@/components/device-profiles/DeviceProfileAssignPanel";
import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";
import { useHqToast } from "@/hooks/useHqToast";
import { getDevice, listDevices } from "@/lib/api/devices";
import type { DeviceResponse } from "@/lib/api/devices-schemas";

export function DevicesIndexPage() {
  const router = useRouter();
  const { showToast } = useHqToast();
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setDevices(await listDevices());
      } catch (err) {
        showToast(err instanceof Error ? err.message : "Gagal memuat perangkat", "error");
      } finally {
        setLoading(false);
      }
    })();
  }, [showToast]);

  return (
    <HqPageContent description="Perangkat tenant — buka detail untuk assign device profile.">
      <CreamCard className="overflow-x-auto p-0">
        <table className="min-w-full text-sm">
          <thead className="border-b border-cream-border bg-cream-alt text-xs uppercase text-ink-tertiary">
            <tr>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">Type</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-left">Profile</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-ink-secondary">
                  Memuat…
                </td>
              </tr>
            ) : null}
            {devices.map((d) => (
              <tr
                key={d.id}
                className="cursor-pointer border-b border-cream-border hover:bg-cream-muted/50"
                onClick={() => router.push(`/devices/${d.id}`)}
              >
                <td className="px-4 py-3 font-medium">{d.name}</td>
                <td className="px-4 py-3">{d.device_type}</td>
                <td className="px-4 py-3">{d.status}</td>
                <td className="px-4 py-3 font-mono text-xs">{d.profile_id ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CreamCard>
      <Link href="/device-profiles" className="text-sm text-accent-cobalt underline">
        Kelola device profiles
      </Link>
    </HqPageContent>
  );
}

export function DeviceDetailPage({ deviceId }: { deviceId: string }) {
  const { showToast } = useHqToast();
  const [device, setDevice] = useState<DeviceResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    try {
      setDevice(await getDevice(deviceId));
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal memuat perangkat", "error");
    } finally {
      setLoading(false);
    }
  }, [deviceId, showToast]);

  useEffect(() => {
    void reload();
  }, [reload]);

  if (loading || !device) {
    return (
      <HqPageContent>
        <p className="text-sm text-ink-secondary">{loading ? "Memuat…" : "Perangkat tidak ditemukan."}</p>
      </HqPageContent>
    );
  }

  return (
    <HqPageContent description={`Perangkat · ${device.name}`}>
      <CreamCard className="p-5">
        <h2 className="text-lg font-semibold text-ink-primary">{device.name}</h2>
        <p className="mt-1 text-sm text-ink-secondary">
          {device.device_type} · {device.status}
        </p>
      </CreamCard>
      <DeviceProfileAssignPanel device={device} onAssigned={() => void reload()} />
    </HqPageContent>
  );
}
