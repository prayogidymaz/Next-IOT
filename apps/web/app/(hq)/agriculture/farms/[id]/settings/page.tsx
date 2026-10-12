"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { AgriFarmLayout } from "@/components/agriculture/AgriFarmLayout";
import {
  fetchNotificationSettings,
  isValidIndonesiaWhatsApp,
  saveNotificationSettings,
  testFarmNotification,
} from "@/lib/agriculture/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

export default function FarmSettingsPage() {
  const farmId = String(useParams().id ?? "");
  const [prefs, setPrefs] = useState({
    disease_alerts: true,
    irrigation: true,
    battery: true,
    weather: true,
    harvest: true,
    whatsapp_number: "",
  });

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    void fetchNotificationSettings(token, farmId).then(setPrefs);
  }, [farmId]);

  const [message, setMessage] = useState<string | null>(null);

  const save = () => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    if (prefs.whatsapp_number && !isValidIndonesiaWhatsApp(prefs.whatsapp_number)) {
      setMessage("Nomor WhatsApp tidak valid (format Indonesia).");
      return;
    }
    void saveNotificationSettings(token, farmId, prefs).then(() => setMessage("Pengaturan disimpan."));
  };

  const testSend = () => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    void testFarmNotification(token, farmId).then((r) =>
      setMessage(r.sent ? "Pesan uji terkirim." : "Gagal mengirim (cek nomor & token Fonnte)."),
    );
  };

  return (
    <AgriFarmLayout farmId={farmId} title="Notification settings">
      <div className="max-w-md space-y-3 rounded-xl border p-4">
        {(Object.keys(prefs) as (keyof typeof prefs)[]).map((key) =>
          key === "whatsapp_number" ? (
            <label key={key} className="block text-sm">
              WhatsApp
              <input
                className="mt-1 w-full rounded border px-2 py-1"
                value={prefs.whatsapp_number}
                onChange={(e) => setPrefs({ ...prefs, whatsapp_number: e.target.value })}
              />
            </label>
          ) : (
            <label key={key} className="flex items-center gap-2 text-sm capitalize">
              <input
                type="checkbox"
                checked={prefs[key]}
                onChange={(e) => setPrefs({ ...prefs, [key]: e.target.checked })}
              />
              {key.replace("_", " ")}
            </label>
          ),
        )}
        <div className="flex flex-wrap gap-2">
          <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={save}>
            Save
          </button>
          <button type="button" className="rounded border px-3 py-2 text-sm" onClick={testSend}>
            Test send WA
          </button>
        </div>
        {message ? <p className="text-sm text-ink-secondary">{message}</p> : null}
      </div>
    </AgriFarmLayout>
  );
}
