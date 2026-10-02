"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ProfileStatusBadge } from "@/components/device-profiles/profile-badges";
import { CreamCard } from "@/components/ui/CreamCard";
import { useHqToast } from "@/hooks/useHqToast";
import { useHqUser } from "@/hooks/useHqUser";
import { assignDeviceProfile, listDeviceProfiles } from "@/lib/api/deviceProfiles";
import type { DeviceProfile } from "@/lib/api/device-profiles-schemas";
import type { DeviceResponse } from "@/lib/api/devices-schemas";
import { RBAC_DENIED_MESSAGE } from "@/lib/hq/rbac";

type DeviceProfileAssignPanelProps = {
  device: DeviceResponse;
  onAssigned: () => void;
};

export function DeviceProfileAssignPanel({ device, onAssigned }: DeviceProfileAssignPanelProps) {
  const { canWriteProfiles } = useHqUser();
  const { showToast } = useHqToast();
  const [published, setPublished] = useState<DeviceProfile[]>([]);
  const [selected, setSelected] = useState<string>(device.profile_id ?? "");
  const [attached, setAttached] = useState<DeviceProfile | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const rows = await listDeviceProfiles({ status: "published" });
      setPublished(rows);
      if (device.profile_id) {
        const match = rows.find((r) => r.id === device.profile_id);
        setAttached(match ?? null);
      } else {
        setAttached(null);
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal memuat profil", "error");
    }
  }, [device.profile_id, showToast]);

  useEffect(() => {
    void load();
  }, [load]);

  const options = useMemo(
    () => published.filter((p) => p.tenant_id === device.tenant_id),
    [published, device.tenant_id],
  );

  async function onAssign() {
    if (!canWriteProfiles) {
      showToast(RBAC_DENIED_MESSAGE, "error");
      return;
    }
    setBusy(true);
    try {
      await assignDeviceProfile(device.id, selected || null);
      showToast("Profil perangkat diperbarui.", "success");
      onAssigned();
      void load();
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal assign", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <CreamCard className="p-5">
      <h2 className="text-lg font-semibold text-ink-primary">Device Profile</h2>
      {attached ? (
        <p className="mt-2 text-sm text-ink-secondary">
          Terpasang:{" "}
          <span className="font-mono font-medium text-ink-primary">
            {attached.key} v{attached.version}
          </span>{" "}
          <ProfileStatusBadge status={attached.status} />
        </p>
      ) : (
        <p className="mt-2 text-sm text-ink-secondary">Belum ada profil terpasang.</p>
      )}
      <label className="mt-4 block text-sm text-ink-secondary">
        Profile published
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          className="mt-1 w-full rounded-xl border border-cream-border bg-white px-3 py-2 text-sm"
        >
          <option value="">— Tidak ada —</option>
          {options.map((p) => (
            <option key={p.id} value={p.id}>
              {p.key} v{p.version} · {p.name}
            </option>
          ))}
        </select>
      </label>
      <button
        type="button"
        disabled={busy}
        onClick={() => void onAssign()}
        className="mt-4 rounded-xl bg-accent-emerald px-4 py-2 text-sm font-semibold text-white"
      >
        Assign
      </button>
    </CreamCard>
  );
}
