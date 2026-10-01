"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

type MeshNode = {
  node_id: string;
  label: string;
  device_type: string;
  rssi?: number;
  snr?: number;
  battery_pct?: number;
};

const DEMO_NODES: MeshNode[] = [
  { node_id: "CDK-01", label: "Cyberdeck Unit 1", device_type: "cyberdeck", rssi: -82, snr: 9.5, battery_pct: 78 },
  { node_id: "CDK-02", label: "Cyberdeck Unit 2", device_type: "cyberdeck", rssi: -91, snr: 6.2, battery_pct: 64 },
  { node_id: "SW-01", label: "ESP32-S3 Smartwatch", device_type: "lorawan", rssi: -88, snr: 7.8, battery_pct: 52 },
];

function signalColor(rssi?: number) {
  if (rssi == null) return "#6B7280";
  if (rssi > -85) return "#39FF14";
  if (rssi >= -105) return "#FFB000";
  return "#FF3131";
}

export function CyberdeckConsole() {
  const [channel, setChannel] = useState(3);
  const [tx, setTx] = useState(false);
  const [wave, setWave] = useState<number[]>(() => Array.from({ length: 24 }, () => 0.08));
  const [selected, setSelected] = useState("CDK-01");
  const [message, setMessage] = useState("");
  const [lastDispatch, setLastDispatch] = useState<string | null>(null);

  useEffect(() => {
    if (!tx) return;
    const id = window.setInterval(() => {
      setWave(Array.from({ length: 24 }, () => 0.15 + Math.random() * 0.85));
    }, 80);
    return () => window.clearInterval(id);
  }, [tx]);

  const nodes = useMemo(() => DEMO_NODES, []);

  const onPttDown = useCallback(() => setTx(true), []);
  const onPttUp = useCallback(() => {
    setTx(false);
    setWave(Array.from({ length: 24 }, () => 0.08));
  }, []);

  return (
    <div className="min-h-screen bg-black font-mono text-[#E8E8E8]">
      <header className="border-b border-[#1F1F1F] bg-[#0A0A0A] px-4 py-3">
        <h1 className="text-sm font-bold tracking-[0.2em] text-[#FFB000]">CYBERDECK // LoRa PTT CONSOLE</h1>
      </header>
      <main className="grid gap-3 p-3 lg:grid-cols-2">
        <section className="border border-[#1F1F1F] bg-[#0A0A0A] p-4">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-xs font-bold text-[#39FF14]">LoRa PTT VOICE</span>
            <select
              className="border border-[#1F1F1F] bg-black px-2 py-1 text-xs"
              value={channel}
              onChange={(e) => setChannel(Number(e.target.value))}
            >
              {Array.from({ length: 8 }, (_, i) => (
                <option key={i + 1} value={i + 1}>
                  CH {i + 1}
                </option>
              ))}
            </select>
          </div>
          <div className="mb-3 flex h-16 items-end gap-0.5">
            {wave.map((level, i) => (
              <div
                key={i}
                className="flex-1 transition-all duration-75"
                style={{
                  height: `${8 + level * 52}px`,
                  backgroundColor: tx ? "#FFB000" : "rgba(57,255,20,0.35)",
                }}
              />
            ))}
          </div>
          <button
            type="button"
            className={`w-full border py-5 text-xs font-extrabold tracking-widest ${
              tx ? "border-[#FFB000] bg-[#FFB000]/20 text-[#FFB000]" : "border-[#FFB000] text-[#E8E8E8]"
            }`}
            onPointerDown={onPttDown}
            onPointerUp={onPttUp}
            onPointerLeave={onPttUp}
          >
            {tx ? "TRANSMITTING…" : "HOLD TO PTT"}
          </button>
        </section>

        <section className="border border-[#1F1F1F] bg-[#0A0A0A] p-4">
          <h2 className="mb-2 text-xs font-bold text-[#FFB000]">NODE MESH TRACKER</h2>
          <ul className="space-y-2 text-xs">
            {nodes.map((node) => (
              <li key={node.node_id}>
                <button
                  type="button"
                  onClick={() => setSelected(node.node_id)}
                  className={`w-full border p-2 text-left ${selected === node.node_id ? "border-[#39FF14]" : "border-transparent"}`}
                >
                  <div className="font-bold">{node.label}</div>
                  <div className="text-[#6B7280]">
                    {node.node_id} • {node.device_type.toUpperCase()}
                  </div>
                  <div style={{ color: signalColor(node.rssi) }}>
                    RSSI {node.rssi} dBm • SNR {node.snr} dB • BATT {node.battery_pct}%
                  </div>
                </button>
              </li>
            ))}
          </ul>
        </section>

        <section className="border border-[#1F1F1F] bg-[#0A0A0A] p-4 lg:col-span-2">
          <h2 className="mb-2 text-xs font-bold text-[#39FF14]">TEXT & COMMAND DISPATCHER</h2>
          <textarea
            value={message}
            maxLength={160}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Short LoRa message (AES encrypted)"
            className="mb-2 h-20 w-full border border-[#1F1F1F] bg-black p-2 text-xs outline-none focus:border-[#FFB000]"
          />
          <div className="flex gap-2">
            <button
              type="button"
              className="flex-1 border border-[#39FF14] px-3 py-2 text-xs text-[#39FF14]"
              onClick={() => {
                setLastDispatch(`TEXT → ${message}`);
                setMessage("");
              }}
            >
              SEND TEXT
            </button>
            <button
              type="button"
              className="flex-1 bg-[#FF3131] px-3 py-2 text-xs font-bold text-black"
              onClick={() => setLastDispatch("BEACON • EMERGENCY")}
            >
              EMERGENCY BEACON
            </button>
          </div>
          {lastDispatch && <p className="mt-2 text-[11px] text-[#6B7280]">LAST: {lastDispatch}</p>}
        </section>

        <section className="border border-[#1F1F1F] bg-[#0A0A0A] p-4 lg:col-span-2">
          <h2 className="mb-2 text-xs font-bold text-[#FFB000]">HARDWARE HEALTH MONITOR</h2>
          <div className="grid grid-cols-2 gap-2 text-xs md:grid-cols-4">
            {[
              ["CPU TEMP", "54.2 °C"],
              ["RAM USED", "61 %"],
              ["BATTERY", "88 %"],
              ["CRYPTO", "AES-128-GCM"],
            ].map(([k, v]) => (
              <div key={k} className="border border-[#1F1F1F] p-2">
                <div className="text-[#6B7280]">{k}</div>
                <div className="text-[#39FF14]">{v}</div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
