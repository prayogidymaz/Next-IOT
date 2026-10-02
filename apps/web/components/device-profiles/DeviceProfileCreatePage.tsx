"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { SpecEditor } from "@/components/device-profiles/SpecEditor";
import { PROFILE_DOMAINS } from "@/components/device-profiles/profile-badges";
import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";
import { useHqToast } from "@/hooks/useHqToast";
import { useHqUser } from "@/hooks/useHqUser";
import { createDeviceProfile } from "@/lib/api/deviceProfiles";
import type { ProfileDomain, ThingModelSpec } from "@/lib/api/device-profiles-schemas";
import { validateProfileKey, validateThingModelSpec } from "@/lib/device-profiles/validation";
import { RBAC_DENIED_MESSAGE } from "@/lib/hq/rbac";

const EMPTY_SPEC: ThingModelSpec = { telemetry: [], attributes: [], commands: [] };

export function DeviceProfileCreatePage() {
  const router = useRouter();
  const { canWriteProfiles } = useHqUser();
  const { showToast } = useHqToast();
  const [key, setKey] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [domain, setDomain] = useState<ProfileDomain>("generic");
  const [spec, setSpec] = useState<ThingModelSpec>(EMPTY_SPEC);
  const [saving, setSaving] = useState(false);

  async function onSubmit() {
    if (!canWriteProfiles) {
      showToast(RBAC_DENIED_MESSAGE, "error");
      return;
    }
    const keyErr = validateProfileKey(key);
    if (keyErr) {
      showToast(keyErr, "error");
      return;
    }
    const issues = validateThingModelSpec(spec);
    if (issues.length > 0) {
      showToast(issues[0]?.message ?? "Spec tidak valid", "error");
      return;
    }
    setSaving(true);
    try {
      const created = await createDeviceProfile({ key, name, description, domain, spec });
      showToast("Profil draft dibuat.", "success");
      router.push(`/device-profiles/${created.id}`);
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal membuat profil", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <HqPageContent description="Buat device profile draft baru. Publish setelah spec siap.">
      <CreamCard className="grid gap-4 p-5 sm:grid-cols-2">
        <label className="text-sm text-ink-secondary">
          Key
          <input value={key} onChange={(e) => setKey(e.target.value)} className="mt-1 w-full rounded-xl border border-cream-border px-3 py-2" />
        </label>
        <label className="text-sm text-ink-secondary">
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} className="mt-1 w-full rounded-xl border border-cream-border px-3 py-2" />
        </label>
        <label className="text-sm text-ink-secondary sm:col-span-2">
          Description
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="mt-1 w-full rounded-xl border border-cream-border px-3 py-2"
            rows={2}
          />
        </label>
        <label className="text-sm text-ink-secondary">
          Domain
          <select
            value={domain}
            onChange={(e) => setDomain(e.target.value as ProfileDomain)}
            className="mt-1 w-full rounded-xl border border-cream-border px-3 py-2"
          >
            {PROFILE_DOMAINS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>
      </CreamCard>
      <SpecEditor spec={spec} onChange={setSpec} readOnly={false} />
      <button
        type="button"
        disabled={saving}
        onClick={() => void onSubmit()}
        className="rounded-xl bg-accent-emerald px-5 py-2.5 text-sm font-semibold text-white"
      >
        {saving ? "Menyimpan…" : "Create draft"}
      </button>
    </HqPageContent>
  );
}
