"use client";

import { Cpu, Mic, Radio, Server } from "lucide-react";
import { useState } from "react";

import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";

const BOARDS = [
  { id: "esp32s3", label: "ESP32-S3 Edge", icon: Cpu, soft: "bg-accent-violet-soft", color: "text-accent-violet" },
  { id: "orangepi", label: "Orange Pi 5 Pro", icon: Server, soft: "bg-accent-amber-soft", color: "text-accent-amber" },
];

const PINS = [
  { signal: "SX1262 NSS", gpio: "GPIO10" },
  { signal: "SX1262 DIO1", gpio: "GPIO11" },
  { signal: "INMP441 WS", gpio: "GPIO5" },
  { signal: "MAX98357 LRC", gpio: "GPIO16" },
  { signal: "PTT Button", gpio: "GPIO0" },
];

export function FirmwareStudioPage() {
  const [board, setBoard] = useState("esp32s3");
  const [codec2, setCodec2] = useState(true);
  const [lora, setLora] = useState(true);

  return (
    <HqPageContent description="Visual blocks for ESP32-S3 and Orange Pi — pin mapping, Codec2 audio, and LoRa SX1262.">
      <div className="grid gap-6 lg:grid-cols-3">
        <CreamCard className="p-5 lg:col-span-1">
          <h2 className="font-semibold text-ink-primary">Target board</h2>
          <div className="mt-4 space-y-2">
            {BOARDS.map((b) => (
              <button
                key={b.id}
                type="button"
                onClick={() => setBoard(b.id)}
                className={`flex w-full items-center gap-3 rounded-xl border px-3 py-3 text-left transition ${
                  board === b.id
                    ? "border-cream-border bg-cream-muted shadow-sm"
                    : "border-cream-border bg-white hover:bg-cream-muted"
                }`}
              >
                <span className={`rounded-lg p-2 ${b.soft}`}>
                  <b.icon className={`h-5 w-5 ${b.color}`} />
                </span>
                <span className="font-medium text-ink-primary">{b.label}</span>
              </button>
            ))}
          </div>
          <div className="mt-6 space-y-3">
            <label className="flex items-center justify-between gap-3 text-sm">
              <span className="flex items-center gap-2 text-ink-secondary">
                <Mic className="h-4 w-4 text-accent-indigo" />
                Codec2 audio (1200 bit/s)
              </span>
              <input type="checkbox" checked={codec2} onChange={(e) => setCodec2(e.target.checked)} />
            </label>
            <label className="flex items-center justify-between gap-3 text-sm">
              <span className="flex items-center gap-2 text-ink-secondary">
                <Radio className="h-4 w-4 text-accent-cobalt" />
                LoRa SX1262 mesh
              </span>
              <input type="checkbox" checked={lora} onChange={(e) => setLora(e.target.checked)} />
            </label>
          </div>
        </CreamCard>

        <CreamCard className="p-5 lg:col-span-2">
          <h2 className="font-semibold text-ink-primary">Pin mapping canvas</h2>
          <p className="mt-1 text-sm text-ink-secondary">
            Wiring preview for {board === "esp32s3" ? "ESP32-S3" : "Orange Pi"} bridge.
          </p>
          <div className="mt-5 overflow-hidden rounded-2xl border border-cream-border">
            <table className="w-full text-left text-sm">
              <thead className="bg-cream-muted text-ink-secondary">
                <tr>
                  <th className="px-4 py-3 font-medium">Subsystem</th>
                  <th className="px-4 py-3 font-medium">Assignment</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cream-border bg-white">
                {PINS.map((row) => (
                  <tr key={row.signal}>
                    <td className="px-4 py-3 text-ink-primary">{row.signal}</td>
                    <td className="px-4 py-3 font-mono text-xs text-ink-secondary">{row.gpio}</td>
                    <td className="px-4 py-3">
                      <span className="rounded-md bg-accent-emerald-soft px-2 py-0.5 text-xs font-medium text-accent-emerald">
                        Validated
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-5 flex flex-wrap gap-3">
            <button type="button" className="hq-btn-primary">
              Generate PlatformIO bundle
            </button>
            <button type="button" className="hq-btn-soft">
              Push to OTA release
            </button>
          </div>
        </CreamCard>
      </div>
    </HqPageContent>
  );
}
