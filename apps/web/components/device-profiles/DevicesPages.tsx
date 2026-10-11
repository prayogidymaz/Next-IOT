"use client";

import { Grid3X3, LayoutList, Map } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { DeviceProfileAssignPanel } from "@/components/device-profiles/DeviceProfileAssignPanel";
import { AttributesPanel } from "@/components/devices/attributes-panel";
import { MqttCredentialsPanel } from "@/components/devices/mqtt-credentials-panel";
import { RpcPanel } from "@/components/devices/rpc-panel";
import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";
import { useHqToast } from "@/hooks/useHqToast";
import { getDevice, listDevices } from "@/lib/api/devices";
import type { DeviceResponse } from "@/lib/api/devices-schemas";

type DevicesView = "table" | "grid" | "map";

export function DevicesIndexPage() {
  const router = useRouter();
  const { showToast } = useHqToast();
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<DevicesView>("table");
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

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

  const filtered = useMemo(() => {
    return devices.filter((d) => {
      if (statusFilter && d.status !== statusFilter) return false;
      if (!query.trim()) return true;
      const q = query.toLowerCase();
      return d.name.toLowerCase().includes(q) || d.device_type.toLowerCase().includes(q);
    });
  }, [devices, query, statusFilter]);

  return (
    <HqPageContent description="Perangkat tenant — buka detail untuk assign device profile.">
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search name or type…"
          className="min-w-[200px] flex-1 rounded-xl border border-cream-border bg-white px-3 py-2 text-sm"
          aria-label="Search devices"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-xl border border-cream-border bg-white px-3 py-2 text-sm"
          aria-label="Filter by status"
        >
          <option value="">All status</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
        </select>
        <div className="flex rounded-xl border border-cream-border bg-white p-1">
          {(
            [
              ["table", LayoutList],
              ["grid", Grid3X3],
              ["map", Map],
            ] as const
          ).map(([mode, Icon]) => (
            <button
              key={mode}
              type="button"
              aria-pressed={view === mode}
              onClick={() => setView(mode)}
              className={`rounded-lg p-2 ${view === mode ? "bg-cream-muted text-ink-primary" : "text-ink-tertiary"}`}
            >
              <Icon className="h-4 w-4" />
            </button>
          ))}
        </div>
        <button type="button" className="hq-btn-soft text-xs">
          Export CSV
        </button>
      </div>

      {view === "grid" ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((d) => (
            <div key={d.id} role="button" tabIndex={0} className="cursor-pointer" onClick={() => router.push(`/devices/${d.id}`)} onKeyDown={(e) => { if (e.key === "Enter") router.push(`/devices/${d.id}`); }}>
            <CreamCard hover className="p-4">
              <div className="flex items-center justify-between">
                <p className="font-semibold">{d.name}</p>
                <span className="rounded-full bg-cream-muted px-2 py-0.5 text-xs">{d.status}</span>
              </div>
              <p className="mt-1 text-xs text-ink-secondary">{d.device_type}</p>
              <div className="mt-3 h-12 rounded-lg bg-gradient-to-r from-accent-cobalt-soft to-accent-emerald-soft" />
            </CreamCard>
            </div>
          ))}
        </div>
      ) : null}

      {view === "map" ? (
        <CreamCard className="flex h-64 items-center justify-center p-6 text-sm text-ink-secondary">
          Map view — fleet geolocation markers (Leaflet/Mapbox integration).
        </CreamCard>
      ) : null}

      {view === "table" ? (
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
            {filtered.map((d) => (
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
      ) : null}
      <Link href="/device-profiles" className="mt-4 inline-block text-sm text-accent-cobalt underline">
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
      <MqttCredentialsPanel device={device} />
      <AttributesPanel device={device} />
      <RpcPanel device={device} />
    </HqPageContent>
  );
}
