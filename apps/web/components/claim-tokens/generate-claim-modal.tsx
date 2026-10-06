"use client";

import { useEffect, useState, type FormEvent } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import { useHqToast } from "@/hooks/useHqToast";
import type { ClaimToken } from "@/lib/api/claim-tokens-schemas";
import { createClaimToken } from "@/lib/api/claimTokens";
import { listDeviceProfiles } from "@/lib/api/deviceProfiles";
import type { DeviceProfile } from "@/lib/api/device-profiles-schemas";

const DEVICE_TYPES = ["sensor", "actuator", "gateway", "drone", "camera"] as const;
const CATEGORY_SUGGESTIONS = ["smart-farming", "smart-building", "smart-home", "FIELD_SENSORS_LORA"];

type GenerateClaimModalProps = {
  open: boolean;
  onClose: () => void;
  onCreated: (token: ClaimToken) => void;
};

export function GenerateClaimModal({ open, onClose, onCreated }: GenerateClaimModalProps) {
  const { showToast } = useHqToast();
  const [deviceName, setDeviceName] = useState("");
  const [deviceType, setDeviceType] = useState<string>(DEVICE_TYPES[0]);
  const [deviceCategory, setDeviceCategory] = useState(CATEGORY_SUGGESTIONS[0]);
  const [profileId, setProfileId] = useState("");
  const [ttlHours, setTtlHours] = useState(24);
  const [profiles, setProfiles] = useState<DeviceProfile[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!open) return;
    void listDeviceProfiles({ status: "published" })
      .then(setProfiles)
      .catch(() => setProfiles([]));
  }, [open]);

  if (!open) return null;

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    try {
      const created = await createClaimToken({
        device_name: deviceName.trim(),
        device_type: deviceType,
        device_category: (deviceCategory ?? "").trim(),
        profile_id: profileId || null,
        ttl_hours: Math.min(168, Math.max(1, ttlHours)),
      });
      onCreated(created);
      onClose();
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal membuat token", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <CreamCard className="w-full max-w-md p-6">
        <h3 className="text-lg font-semibold text-ink-primary">Generate Claim Token</h3>
        <form className="mt-4 space-y-3" onSubmit={(e) => void submit(e)}>
          <label className="block text-sm">
            Device Name
            <input
              required
              className="mt-1 w-full rounded-lg border border-cream-border px-3 py-2"
              value={deviceName}
              onChange={(e) => setDeviceName(e.target.value)}
            />
          </label>
          <label className="block text-sm">
            Device Type
            <select
              className="mt-1 w-full rounded-lg border border-cream-border px-3 py-2"
              value={deviceType}
              onChange={(e) => setDeviceType(e.target.value)}
            >
              {DEVICE_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm">
            Device Category
            <input
              required
              list="claim-categories"
              className="mt-1 w-full rounded-lg border border-cream-border px-3 py-2"
              value={deviceCategory}
              onChange={(e) => setDeviceCategory(e.target.value)}
            />
            <datalist id="claim-categories">
              {CATEGORY_SUGGESTIONS.map((c) => (
                <option key={c} value={c} />
              ))}
            </datalist>
          </label>
          <label className="block text-sm">
            Device Profile (optional)
            <select
              className="mt-1 w-full rounded-lg border border-cream-border px-3 py-2"
              value={profileId}
              onChange={(e) => setProfileId(e.target.value)}
            >
              <option value="">— none —</option>
              {profiles.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.key} v{p.version}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm">
            TTL Hours (max 168)
            <input
              type="number"
              min={1}
              max={168}
              className="mt-1 w-full rounded-lg border border-cream-border px-3 py-2"
              value={ttlHours}
              onChange={(e) => setTtlHours(Number(e.target.value))}
            />
          </label>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" className="rounded-lg border border-cream-border px-4 py-2 text-sm" onClick={onClose}>
              Batal
            </button>
            <button
              type="submit"
              disabled={busy}
              className="rounded-lg bg-accent-cobalt px-4 py-2 text-sm text-white disabled:opacity-50"
            >
              Generate
            </button>
          </div>
        </form>
      </CreamCard>
    </div>
  );
}
