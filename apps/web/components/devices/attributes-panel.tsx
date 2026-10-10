"use client";

import { useCallback, useEffect, useState } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import type { DeviceAttributeItem } from "@/lib/api/device-attributes-schemas";
import {
  deleteDeviceAttribute,
  listDeviceAttributes,
  putDeviceAttribute,
} from "@/lib/api/device-attributes";
import type { DeviceResponse } from "@/lib/api/devices-schemas";
import { useHqToast } from "@/hooks/useHqToast";
import { useHqUser } from "@/hooks/useHqUser";

type TabScope = "server" | "shared" | "client";

type AttributesPanelProps = {
  device: DeviceResponse;
};

export function AttributesPanel({ device }: AttributesPanelProps) {
  const { showToast } = useHqToast();
  const { canManageMqttCredentials } = useHqUser();
  const canWrite = canManageMqttCredentials;
  const [tab, setTab] = useState<TabScope>("server");
  const [items, setItems] = useState<DeviceAttributeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editKey, setEditKey] = useState("");
  const [editValue, setEditValue] = useState('""');

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      setItems(await listDeviceAttributes(device.id, tab));
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal memuat attributes", "error");
    } finally {
      setLoading(false);
    }
  }, [device.id, tab, showToast]);

  useEffect(() => {
    void reload();
    const timer = setInterval(() => void reload(), 10_000);
    return () => clearInterval(timer);
  }, [reload]);

  async function saveAttribute() {
    if (tab === "client") return;
    try {
      const value = JSON.parse(editValue) as unknown;
      await putDeviceAttribute(device.id, tab, editKey.trim(), value);
      setModalOpen(false);
      setEditKey("");
      setEditValue('""');
      await reload();
      showToast("Attribute disimpan", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal menyimpan", "error");
    }
  }

  async function remove(key: string) {
    try {
      await deleteDeviceAttribute(device.id, tab, key);
      await reload();
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal menghapus", "error");
    }
  }

  return (
    <CreamCard className="mt-4 p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-ink-primary">Device Attributes</h2>
        <div className="flex gap-2 text-sm">
          {(["server", "shared", "client"] as TabScope[]).map((scope) => (
            <button
              key={scope}
              type="button"
              className={`rounded px-3 py-1 ${tab === scope ? "bg-ink-primary text-white" : "bg-cream-muted"}`}
              onClick={() => setTab(scope)}
            >
              {scope}
            </button>
          ))}
        </div>
      </div>
      {tab === "client" ? (
        <p className="mt-2 text-xs text-ink-secondary">Read-only — nilai di-set oleh perangkat (MQTT/HTTP).</p>
      ) : null}
      {canWrite && tab !== "client" ? (
        <button
          type="button"
          className="mt-3 rounded bg-ink-primary px-3 py-1.5 text-sm text-white"
          onClick={() => setModalOpen(true)}
        >
          + Add
        </button>
      ) : null}
      {loading ? (
        <p className="mt-4 text-sm text-ink-secondary">Memuat…</p>
      ) : (
        <table className="mt-4 w-full text-left text-sm">
          <thead>
            <tr className="border-b border-cream-border text-ink-secondary">
              <th className="py-2">Key</th>
              <th>Value</th>
              <th>Updated</th>
              <th>Source</th>
              {canWrite && tab !== "client" ? <th /> : null}
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.key} className="border-b border-cream-border/60">
                <td className="py-2 font-mono text-xs">{row.key}</td>
                <td className="max-w-xs truncate font-mono text-xs">
                  {JSON.stringify(row.value)}
                </td>
                <td className="text-xs">{new Date(row.updated_at).toLocaleString()}</td>
                <td className="text-xs">{row.updated_source}</td>
                {canWrite && tab !== "client" ? (
                  <td className="text-right">
                    <button type="button" className="text-xs text-red-600" onClick={() => void remove(row.key)}>
                      Delete
                    </button>
                  </td>
                ) : null}
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {modalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-lg bg-white p-4 shadow-lg">
            <h3 className="font-semibold">Attribute ({tab})</h3>
            <label className="mt-3 block text-xs text-ink-secondary">Key</label>
            <input
              className="mt-1 w-full rounded border px-2 py-1 text-sm"
              value={editKey}
              onChange={(e) => setEditKey(e.target.value)}
            />
            <label className="mt-3 block text-xs text-ink-secondary">Value (JSON)</label>
            <textarea
              className="mt-1 w-full rounded border px-2 py-1 font-mono text-xs"
              rows={5}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
            />
            <div className="mt-4 flex justify-end gap-2">
              <button type="button" className="text-sm" onClick={() => setModalOpen(false)}>Batal</button>
              <button type="button" className="rounded bg-ink-primary px-3 py-1 text-sm text-white" onClick={() => void saveAttribute()}>
                Simpan
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </CreamCard>
  );
}
