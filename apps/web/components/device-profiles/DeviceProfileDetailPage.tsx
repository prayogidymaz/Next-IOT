"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import {
  ProfileDomainBadge,
  ProfileStatusBadge,
  PROFILE_DOMAINS,
} from "@/components/device-profiles/profile-badges";
import { SpecEditor } from "@/components/device-profiles/SpecEditor";
import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";
import { useHqToast } from "@/hooks/useHqToast";
import { useHqUser } from "@/hooks/useHqUser";
import {
  archiveDeviceProfile,
  getDeviceProfile,
  newVersionDeviceProfile,
  patchDeviceProfile,
  publishDeviceProfile,
} from "@/lib/api/deviceProfiles";
import type { DeviceProfile, ProfileDomain, ThingModelSpec } from "@/lib/api/device-profiles-schemas";
import { validateThingModelSpec } from "@/lib/device-profiles/validation";
import { RBAC_DENIED_MESSAGE } from "@/lib/hq/rbac";

type DeviceProfileDetailPageProps = {
  profileId: string;
};

export function DeviceProfileDetailPage({ profileId }: DeviceProfileDetailPageProps) {
  const router = useRouter();
  const { canWriteProfiles } = useHqUser();
  const { showToast } = useHqToast();
  const [profile, setProfile] = useState<DeviceProfile | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [domain, setDomain] = useState<ProfileDomain>("generic");
  const [spec, setSpec] = useState<ThingModelSpec>({ telemetry: [], attributes: [], commands: [] });
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const readOnly = profile?.status === "published" || profile?.status === "archived";

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getDeviceProfile(profileId);
      setProfile(data);
      setName(data.name);
      setDescription(data.description);
      setDomain(data.domain);
      setSpec(data.spec);
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal memuat profil", "error");
    } finally {
      setLoading(false);
    }
  }, [profileId, showToast]);

  useEffect(() => {
    void load();
  }, [load]);

  function guardWrite(action: () => void) {
    if (!canWriteProfiles) {
      showToast(RBAC_DENIED_MESSAGE, "error");
      return;
    }
    action();
  }

  async function onSave() {
    if (!profile || readOnly) return;
    const issues = validateThingModelSpec(spec);
    if (issues.length > 0) {
      showToast(issues[0]?.message ?? "Spec tidak valid", "error");
      return;
    }
    setBusy(true);
    try {
      const updated = await patchDeviceProfile(profile.id, { name, description, domain, spec });
      setProfile(updated);
      showToast("Perubahan disimpan.", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal menyimpan", "error");
    } finally {
      setBusy(false);
    }
  }

  async function onPublish() {
    if (!profile) return;
    setBusy(true);
    try {
      const updated = await publishDeviceProfile(profile.id);
      setProfile(updated);
      showToast("Profil published.", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal publish", "error");
    } finally {
      setBusy(false);
    }
  }

  async function onNewVersion() {
    if (!profile) return;
    setBusy(true);
    try {
      const draft = await newVersionDeviceProfile(profile.id);
      showToast("Draft versi baru dibuat.", "success");
      router.push(`/device-profiles/${draft.id}`);
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal buat versi baru", "error");
    } finally {
      setBusy(false);
    }
  }

  async function onArchive() {
    if (!profile) return;
    setBusy(true);
    try {
      const updated = await archiveDeviceProfile(profile.id);
      setProfile(updated);
      showToast("Profil diarsipkan.", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Gagal arsip", "error");
    } finally {
      setBusy(false);
    }
  }

  if (loading || !profile) {
    return (
      <HqPageContent>
        <p className="text-sm text-ink-secondary">{loading ? "Memuat profil…" : "Profil tidak ditemukan."}</p>
      </HqPageContent>
    );
  }

  return (
    <HqPageContent description={`Thing model · ${profile.key} v${profile.version}`}>
      <CreamCard className="flex flex-wrap items-start justify-between gap-4 p-5">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-semibold text-ink-primary">{profile.name}</h2>
            <ProfileStatusBadge status={profile.status} />
            <ProfileDomainBadge domain={profile.domain} />
          </div>
          <p className="mt-1 font-mono text-xs text-ink-secondary">
            {profile.key} · v{profile.version}
          </p>
          {readOnly ? (
            <p className="mt-2 text-xs font-medium text-accent-amber">VIEW-ONLY — status {profile.status}</p>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-2">
          {profile.status === "draft" ? (
            <>
              <button
                type="button"
                disabled={busy}
                onClick={() => guardWrite(() => void onSave())}
                className="rounded-xl border border-cream-border bg-white px-4 py-2 text-sm font-medium"
              >
                Save
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => guardWrite(() => void onPublish())}
                className="rounded-xl bg-accent-emerald px-4 py-2 text-sm font-semibold text-white"
              >
                Publish
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => guardWrite(() => void onArchive())}
                className="rounded-xl border border-red-200 px-4 py-2 text-sm text-red-700"
              >
                Archive
              </button>
            </>
          ) : null}
          {profile.status === "published" ? (
            <>
              <button
                type="button"
                disabled={busy}
                onClick={() => guardWrite(() => void onNewVersion())}
                className="rounded-xl bg-accent-cobalt px-4 py-2 text-sm font-semibold text-white"
              >
                New Version
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => guardWrite(() => void onArchive())}
                className="rounded-xl border border-red-200 px-4 py-2 text-sm text-red-700"
              >
                Archive
              </button>
            </>
          ) : null}
        </div>
      </CreamCard>

      <CreamCard className="grid gap-4 p-5 sm:grid-cols-2">
        <label className="text-sm text-ink-secondary">
          Name
          <input
            disabled={readOnly}
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full rounded-xl border border-cream-border px-3 py-2 disabled:bg-cream-muted"
          />
        </label>
        <label className="text-sm text-ink-secondary">
          Domain
          <select
            disabled={readOnly}
            value={domain}
            onChange={(e) => setDomain(e.target.value as ProfileDomain)}
            className="mt-1 w-full rounded-xl border border-cream-border px-3 py-2 disabled:bg-cream-muted"
          >
            {PROFILE_DOMAINS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm text-ink-secondary sm:col-span-2">
          Description
          <textarea
            disabled={readOnly}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="mt-1 w-full rounded-xl border border-cream-border px-3 py-2 disabled:bg-cream-muted"
            rows={2}
          />
        </label>
      </CreamCard>

      <SpecEditor spec={spec} onChange={setSpec} readOnly={readOnly} />
    </HqPageContent>
  );
}
