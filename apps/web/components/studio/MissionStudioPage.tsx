"use client";

import { MapPin, Navigation, Plane } from "lucide-react";
import { useState } from "react";

import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";

const WAYPOINTS = [
  { id: "WP-1", lat: "-6.2088", lng: "106.8456", label: "Depot Alpha" },
  { id: "WP-2", lat: "-6.2142", lng: "106.8510", label: "Delivery Node B" },
  { id: "WP-3", lat: "-6.2195", lng: "106.8398", label: "Patrol checkpoint" },
];

export function MissionStudioPage() {
  const [mode, setMode] = useState<"drone" | "robot">("drone");

  return (
    <HqPageContent description="GIS waypoint planner for drone delivery and robotic patrol corridors.">
      <div className="mb-4 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setMode("drone")}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
            mode === "drone" ? "bg-accent-amber text-white" : "bg-cream-muted text-ink-secondary"
          }`}
        >
          <Plane className="mr-1 inline h-4 w-4" />
          Drone delivery
        </button>
        <button
          type="button"
          onClick={() => setMode("robot")}
          className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
            mode === "robot" ? "bg-accent-violet text-white" : "bg-cream-muted text-ink-secondary"
          }`}
        >
          <Navigation className="mr-1 inline h-4 w-4" />
          Robotics patrol
        </button>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <CreamCard className="relative min-h-[320px] overflow-hidden lg:col-span-3">
          <div className="absolute inset-0 bg-[linear-gradient(#ecece8_1px,transparent_1px),linear-gradient(90deg,#ecece8_1px,transparent_1px)] bg-[size:24px_24px]" />
          <div className="absolute inset-0 bg-gradient-to-br from-accent-cobalt-soft/40 via-transparent to-accent-amber-soft/30" />
          <div className="relative flex h-full flex-col justify-between p-6">
            <div>
              <p className="text-sm font-medium text-ink-secondary">GIS canvas (placeholder)</p>
              <h3 className="mt-1 text-xl font-semibold text-ink-primary">
                {mode === "drone" ? "Last-mile air corridor" : "Factory floor patrol"}
              </h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {WAYPOINTS.map((wp, i) => (
                <span
                  key={wp.id}
                  className="inline-flex items-center gap-1 rounded-full border border-cream-border bg-white/90 px-3 py-1 text-xs shadow-sm"
                >
                  <MapPin className={`h-3.5 w-3.5 ${i === 0 ? "text-accent-emerald" : "text-accent-amber"}`} />
                  {wp.label}
                </span>
              ))}
            </div>
          </div>
        </CreamCard>

        <CreamCard className="p-5 lg:col-span-2">
          <h2 className="font-semibold text-ink-primary">Waypoint list</h2>
          <ul className="mt-4 space-y-3">
            {WAYPOINTS.map((wp) => (
              <li
                key={wp.id}
                className="rounded-xl border border-cream-border bg-cream-alt px-3 py-3 text-sm"
              >
                <p className="font-medium text-ink-primary">
                  {wp.id} — {wp.label}
                </p>
                <p className="mt-1 font-mono text-xs text-ink-secondary">
                  {wp.lat}, {wp.lng}
                </p>
              </li>
            ))}
          </ul>
          <button type="button" className="hq-btn-primary mt-5 w-full">
            Export mission JSON
          </button>
        </CreamCard>
      </div>
    </HqPageContent>
  );
}
