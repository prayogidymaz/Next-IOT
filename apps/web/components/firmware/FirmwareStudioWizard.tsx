"use client";

import { useCallback, useEffect, useState } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import { downloadFirmwareZip, listDeviceProfiles, previewFirmware } from "@/lib/api/firmware-studio";

type DeviceProfile = { id: string; name: string; key: string };

type SensorRow = { metric: string; driver: string; pin: number };

const DEFAULT_SENSORS: SensorRow[] = [{ metric: "temperature", driver: "dht22", pin: 4 }];

export function FirmwareStudioWizard() {
  const [profiles, setProfiles] = useState<DeviceProfile[]>([]);
  const [profileId, setProfileId] = useState("");
  const [preview, setPreview] = useState("");
  const [wifiSsid, setWifiSsid] = useState("TestWifi");
  const [wifiPassword, setWifiPassword] = useState("testpass");
  const [brokerHost, setBrokerHost] = useState("192.168.1.100");
  const [enableOta, setEnableOta] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void listDeviceProfiles()
      .then(setProfiles)
      .catch(() => setProfiles([]));
  }, []);

  const buildConfig = useCallback(
    () => ({
      mcu: "esp32-s3",
      framework: "platformio",
      wifi_ssid: wifiSsid,
      wifi_password: wifiPassword,
      broker_host: brokerHost,
      broker_port: 1883,
      publish_interval_s: 10,
      enable_ota: enableOta,
      include_credentials: false,
      sensors: DEFAULT_SENSORS,
    }),
    [wifiSsid, wifiPassword, brokerHost, enableOta],
  );

  const onPreview = async () => {
    if (!profileId) {
      setError("Select a device profile");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const res = await previewFirmware({ device_profile_id: profileId, config: buildConfig() });
      setPreview(res.main_cpp);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Preview failed");
    } finally {
      setBusy(false);
    }
  };

  const onDownload = async () => {
    if (!profileId) {
      setError("Select a device profile");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const blob = await downloadFirmwareZip({ device_profile_id: profileId, config: buildConfig() });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "next-iot-firmware.zip";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Download failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <CreamCard className="space-y-4 p-5">
        <h2 className="font-semibold text-ink-primary">1. Device profile</h2>
        <select
          className="w-full rounded-lg border border-cream-border px-3 py-2"
          value={profileId}
          onChange={(e) => setProfileId(e.target.value)}
        >
          <option value="">Select profile…</option>
          {profiles.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} ({p.key})
            </option>
          ))}
        </select>
        <h2 className="font-semibold text-ink-primary">2. Connectivity</h2>
        <input
          className="w-full rounded-lg border border-cream-border px-3 py-2"
          placeholder="WiFi SSID"
          value={wifiSsid}
          onChange={(e) => setWifiSsid(e.target.value)}
        />
        <input
          className="w-full rounded-lg border border-cream-border px-3 py-2"
          type="password"
          placeholder="WiFi password"
          value={wifiPassword}
          onChange={(e) => setWifiPassword(e.target.value)}
        />
        <input
          className="w-full rounded-lg border border-cream-border px-3 py-2"
          placeholder="MQTT broker host"
          value={brokerHost}
          onChange={(e) => setBrokerHost(e.target.value)}
        />
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={enableOta} onChange={(e) => setEnableOta(e.target.checked)} />
          Enable OTA in generated firmware
        </label>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={busy}
            onClick={() => void onPreview()}
            className="rounded-lg bg-accent-cobalt px-4 py-2 text-sm font-medium text-white"
          >
            Preview code
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => void onDownload()}
            className="rounded-lg border border-cream-border px-4 py-2 text-sm font-medium"
          >
            Download ZIP
          </button>
        </div>
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
      </CreamCard>
      <CreamCard className="p-5">
        <h2 className="font-semibold text-ink-primary">Generated main.cpp preview</h2>
        <pre className="mt-3 max-h-[480px] overflow-auto rounded-lg bg-ink-primary/5 p-3 text-xs">
          {preview || "Run preview to see generated source."}
        </pre>
      </CreamCard>
    </div>
  );
}
