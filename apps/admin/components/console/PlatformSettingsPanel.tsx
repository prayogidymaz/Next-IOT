"use client";

import { useCallback, useEffect, useState } from "react";

import { AdminCard } from "@/components/ui/AdminCard";
import { fetchPlatformSettings, updatePlatformSettings } from "@/lib/api/super-admin-extended";

const TABS = [
  { id: "general", label: "General" },
  { id: "email", label: "Email" },
  { id: "payment", label: "Payment" },
  { id: "mqtt", label: "MQTT" },
  { id: "security", label: "Security" },
  { id: "notifications", label: "Notifications" },
] as const;

type SettingsTab = (typeof TABS)[number]["id"];

type SectionMap = Record<string, Record<string, unknown>>;

function str(sections: SectionMap, section: string, key: string, fallback = ""): string {
  const v = sections[section]?.[key];
  return typeof v === "string" ? v : typeof v === "number" ? String(v) : fallback;
}

function num(sections: SectionMap, section: string, key: string, fallback = 0): number {
  const v = sections[section]?.[key];
  return typeof v === "number" ? v : typeof v === "string" ? Number(v) || fallback : fallback;
}

function bool(sections: SectionMap, section: string, key: string, fallback = false): boolean {
  const v = sections[section]?.[key];
  return typeof v === "boolean" ? v : fallback;
}

function fieldLabel(text: string) {
  return <span className="text-sm text-slate-600">{text}</span>;
}

function textInput(
  value: string,
  onChange: (v: string) => void,
  props?: { type?: string; placeholder?: string },
) {
  return (
    <input
      type={props?.type ?? "text"}
      className="admin-input mt-1 w-full"
      value={value}
      placeholder={props?.placeholder}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}

export function PlatformSettingsPanel() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("general");
  const [draft, setDraft] = useState<SectionMap>({});
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    const s = await fetchPlatformSettings();
    setDraft(s.sections);
  }, []);

  useEffect(() => {
    void load().catch(() => setMessage("Failed to load settings"));
  }, [load]);

  function patchSection(section: SettingsTab, patch: Record<string, unknown>) {
    setDraft((prev) => ({
      ...prev,
      [section]: { ...(prev[section] ?? {}), ...patch },
    }));
  }

  async function saveTab(section: SettingsTab) {
    setSaving(true);
    setMessage(null);
    try {
      await updatePlatformSettings({ [section]: draft[section] ?? {} });
      await load();
      setMessage(`${section.charAt(0).toUpperCase()}${section.slice(1)} settings saved`);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  const d = draft;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-1 border-b border-slate-200 dark:border-slate-700">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`border-b-2 px-4 py-2 text-xs font-semibold uppercase tracking-wide transition-colors ${
              activeTab === tab.id
                ? "border-blue-800 text-blue-800"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {message ? <p className="text-sm text-slate-600">{message}</p> : null}

      {activeTab === "general" ? (
        <AdminCard className="space-y-4 p-5">
          <label className="block">
            {fieldLabel("Platform name")}
            {textInput(str(d, "general", "platform_name"), (v) => patchSection("general", { platform_name: v }))}
          </label>
          <label className="block">
            {fieldLabel("Support email")}
            {textInput(str(d, "general", "support_email"), (v) => patchSection("general", { support_email: v }), {
              type: "email",
            })}
          </label>
          <label className="block">
            {fieldLabel("Timezone")}
            {textInput(str(d, "general", "timezone", "Asia/Jakarta"), (v) => patchSection("general", { timezone: v }))}
          </label>
          <label className="block">
            {fieldLabel("Default language")}
            {textInput(str(d, "general", "default_language", "id"), (v) =>
              patchSection("general", { default_language: v }),
            )}
          </label>
          <label className="block">
            {fieldLabel("Logo URL")}
            {textInput(str(d, "general", "logo_url"), (v) => patchSection("general", { logo_url: v }), {
              placeholder: "https://…",
            })}
          </label>
          <button
            type="button"
            disabled={saving}
            className="rounded-md bg-blue-800 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            onClick={() => void saveTab("general")}
          >
            Save general
          </button>
        </AdminCard>
      ) : null}

      {activeTab === "email" ? (
        <AdminCard className="space-y-4 p-5">
          <label className="block">
            {fieldLabel("SMTP host")}
            {textInput(str(d, "email", "smtp_host"), (v) => patchSection("email", { smtp_host: v }))}
          </label>
          <label className="block">
            {fieldLabel("SMTP port")}
            {textInput(String(num(d, "email", "smtp_port", 587)), (v) =>
              patchSection("email", { smtp_port: Number(v) || 587 }),
            )}
          </label>
          <label className="block">
            {fieldLabel("SMTP user")}
            {textInput(str(d, "email", "smtp_user"), (v) => patchSection("email", { smtp_user: v }))}
          </label>
          <label className="block">
            {fieldLabel("SMTP password")}
            {textInput(str(d, "email", "smtp_password"), (v) => patchSection("email", { smtp_password: v }), {
              type: "password",
            })}
          </label>
          <label className="block">
            {fieldLabel("From name")}
            {textInput(str(d, "email", "from_name"), (v) => patchSection("email", { from_name: v }))}
          </label>
          <label className="block">
            {fieldLabel("From email")}
            {textInput(str(d, "email", "from_address"), (v) => patchSection("email", { from_address: v }), {
              type: "email",
            })}
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              disabled={saving}
              className="rounded-md bg-blue-800 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
              onClick={() => void saveTab("email")}
            >
              Save email
            </button>
            <button type="button" className="rounded-md border border-slate-200 px-4 py-2 text-sm">
              Send test email
            </button>
          </div>
        </AdminCard>
      ) : null}

      {activeTab === "payment" ? (
        <AdminCard className="space-y-4 p-5">
          <label className="block">
            {fieldLabel("Midtrans server key")}
            {textInput(str(d, "payment", "midtrans_server_key"), (v) =>
              patchSection("payment", { midtrans_server_key: v }),
            )}
          </label>
          <label className="block">
            {fieldLabel("Midtrans client key")}
            {textInput(str(d, "payment", "midtrans_client_key"), (v) =>
              patchSection("payment", { midtrans_client_key: v }),
            )}
          </label>
          <label className="block">
            {fieldLabel("Xendit API key")}
            {textInput(str(d, "payment", "xendit_secret_key"), (v) =>
              patchSection("payment", { xendit_secret_key: v }),
            )}
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={bool(d, "payment", "sandbox_mode", true)}
              onChange={(e) => patchSection("payment", { sandbox_mode: e.target.checked })}
            />
            Sandbox mode
          </label>
          <button
            type="button"
            disabled={saving}
            className="rounded-md bg-blue-800 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            onClick={() => void saveTab("payment")}
          >
            Save payment
          </button>
        </AdminCard>
      ) : null}

      {activeTab === "mqtt" ? (
        <AdminCard className="space-y-4 p-5">
          <label className="block">
            {fieldLabel("Broker URL")}
            {textInput(str(d, "mqtt", "broker_url", "mqtt://emqx:1883"), (v) => patchSection("mqtt", { broker_url: v }))}
          </label>
          <label className="block">
            {fieldLabel("Broker host")}
            {textInput(str(d, "mqtt", "broker_host"), (v) => patchSection("mqtt", { broker_host: v }))}
          </label>
          <label className="block">
            {fieldLabel("Broker port")}
            {textInput(String(num(d, "mqtt", "broker_port", 1883)), (v) =>
              patchSection("mqtt", { broker_port: Number(v) || 1883 }),
            )}
          </label>
          <label className="block">
            {fieldLabel("MQTT auth URL")}
            {textInput(str(d, "mqtt", "mqtt_auth_url"), (v) => patchSection("mqtt", { mqtt_auth_url: v }))}
          </label>
          <label className="block">
            {fieldLabel("Max connections per tenant")}
            {textInput(String(num(d, "mqtt", "max_connections_per_tenant", 500)), (v) =>
              patchSection("mqtt", { max_connections_per_tenant: Number(v) || 500 }),
            )}
          </label>
          <button
            type="button"
            disabled={saving}
            className="rounded-md bg-blue-800 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            onClick={() => void saveTab("mqtt")}
          >
            Save MQTT
          </button>
        </AdminCard>
      ) : null}

      {activeTab === "security" ? (
        <AdminCard className="space-y-4 p-5">
          <label className="block">
            {fieldLabel("Minimum password length")}
            {textInput(String(num(d, "security", "password_min_length", 12)), (v) =>
              patchSection("security", { password_min_length: Number(v) || 12 }),
            )}
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={bool(d, "security", "require_uppercase")}
              onChange={(e) => patchSection("security", { require_uppercase: e.target.checked })}
            />
            Require uppercase
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={bool(d, "security", "require_number")}
              onChange={(e) => patchSection("security", { require_number: e.target.checked })}
            />
            Require number
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={bool(d, "security", "require_special")}
              onChange={(e) => patchSection("security", { require_special: e.target.checked })}
            />
            Require special character
          </label>
          <label className="block">
            {fieldLabel("Session timeout (minutes)")}
            {textInput(String(num(d, "security", "session_timeout_minutes", 60)), (v) =>
              patchSection("security", { session_timeout_minutes: Number(v) || 60 }),
            )}
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={bool(d, "security", "require_2fa")}
              onChange={(e) => patchSection("security", { require_2fa: e.target.checked })}
            />
            Enforce 2FA for tenant admins
          </label>
          <button
            type="button"
            disabled={saving}
            className="rounded-md bg-blue-800 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            onClick={() => void saveTab("security")}
          >
            Save security
          </button>
        </AdminCard>
      ) : null}

      {activeTab === "notifications" ? (
        <AdminCard className="space-y-4 p-5">
          <label className="block">
            {fieldLabel("Default notification provider")}
            {textInput(str(d, "notifications", "default_provider", "email"), (v) =>
              patchSection("notifications", { default_provider: v }),
            )}
          </label>
          <label className="block">
            {fieldLabel("Fonnte token")}
            {textInput(str(d, "notifications", "fonnte_token"), (v) => patchSection("notifications", { fonnte_token: v }))}
          </label>
          <label className="block">
            {fieldLabel("Telegram bot token")}
            {textInput(str(d, "notifications", "telegram_bot_token"), (v) =>
              patchSection("notifications", { telegram_bot_token: v }),
            )}
          </label>
          <label className="block">
            {fieldLabel("FCM server key")}
            {textInput(str(d, "notifications", "fcm_server_key"), (v) =>
              patchSection("notifications", { fcm_server_key: v }),
            )}
          </label>
          <label className="block">
            {fieldLabel("Rate limit (messages / hour)")}
            {textInput(String(num(d, "notifications", "rate_limit_per_hour", 100)), (v) =>
              patchSection("notifications", { rate_limit_per_hour: Number(v) || 100 }),
            )}
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={bool(d, "notifications", "default_email", true)}
              onChange={(e) => patchSection("notifications", { default_email: e.target.checked })}
            />
            Email notifications enabled by default
          </label>
          <button
            type="button"
            disabled={saving}
            className="rounded-md bg-blue-800 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            onClick={() => void saveTab("notifications")}
          >
            Save notifications
          </button>
        </AdminCard>
      ) : null}
    </div>
  );
}
