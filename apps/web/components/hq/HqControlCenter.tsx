"use client";

import { AlertOctagon, MapPin, Radio, Wifi } from "lucide-react";
import { useCallback, useMemo, useRef, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";
import {
  useControlCenterStream,
  type ControlCenterRemoteSync,
} from "@/hooks/useControlCenterStream";
import { CONTROL_CENTER_ACTUATORS, INITIAL_FLEET } from "@/lib/control-center/config";
import { allRelaysOff, buildInitialRelayState } from "@/lib/control-center/relay-state";
import { HQ_DOMAINS, type HqDomainId } from "@/lib/hq/domains";
import { useHqShell } from "@/lib/hq/hq-shell-context";

export function HqControlCenter() {
  const { tenant, domainId, setDomainId } = useHqShell();
  const [filterDomain, setFilterDomain] = useState<HqDomainId>(domainId);
  const [relayState, setRelayState] = useState<Record<string, boolean>>(buildInitialRelayState);
  const [estop, setEstop] = useState(false);
  const relayStateRef = useRef(relayState);
  const estopRef = useRef(estop);
  relayStateRef.current = relayState;
  estopRef.current = estop;

  const remoteSyncRef = useRef<ControlCenterRemoteSync | null>(null);
  remoteSyncRef.current = {
    applyRelayToggle: (relayId, on) => {
      setRelayState((prev) => ({ ...prev, [relayId]: on }));
    },
    applyEmergencyStop: () => {
      setEstop(true);
      setRelayState((prev) => allRelaysOff(prev));
    },
  };

  const { connected, series, audit, fleet, publishRelayToggle, publishEmergencyStop, pushAudit } =
    useControlCenterStream(filterDomain, remoteSyncRef);

  const toggleRelay = useCallback(
    (relayId: string) => {
      if (estopRef.current) return;
      const next = !Boolean(relayStateRef.current[relayId]);
      setRelayState((prev) => ({ ...prev, [relayId]: next }));
      publishRelayToggle(relayId, next);
    },
    [publishRelayToggle],
  );

  const toggleEstop = useCallback(() => {
    setEstop((prev) => {
      const next = !prev;
      if (next) {
        setRelayState((s) => allRelaysOff(s));
        publishEmergencyStop();
      } else {
        pushAudit("E-STOP cleared — actuators may be operated again.", "info");
      }
      return next;
    });
  }, [publishEmergencyStop, pushAudit]);

  const actuators = useMemo(
    () => CONTROL_CENTER_ACTUATORS.filter((a) => a.domain === filterDomain),
    [filterDomain],
  );

  const fleetMarkers = useMemo(() => {
    const base = INITIAL_FLEET.filter((f) => f.domain === filterDomain);
    if (fleet.length === 0) return base;
    return base.map((b, i) => {
      const live = fleet[i % fleet.length];
      return live ? { ...b, lat: live.lat, lon: live.lon } : b;
    });
  }, [filterDomain, fleet]);

  return (
    <HqPageContent description={`Tactical command grid · ${tenant} · live telemetry stream`}>
      <CreamCard className="p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold text-ink-primary">Domain filter</p>
            <p className="text-xs text-ink-secondary">Scope widgets to operational theater</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {HQ_DOMAINS.map((d) => (
              <button
                key={d.id}
                type="button"
                onClick={() => {
                  setFilterDomain(d.id);
                  setDomainId(d.id);
                }}
                className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${
                  filterDomain === d.id
                    ? "bg-ink-primary text-white shadow-sm"
                    : "bg-cream-muted text-ink-secondary hover:bg-cream-alt"
                }`}
              >
                {d.emoji} {d.label}
              </button>
            ))}
          </div>
          <span
            className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold ${
              connected ? "bg-accent-emerald-soft text-accent-emerald" : "bg-accent-amber-soft text-accent-amber"
            }`}
          >
            <Wifi className="h-3 w-3" />
            {connected ? "WS live" : "WS reconnecting"}
          </span>
        </div>
      </CreamCard>

      <CreamCard className="border-red-200 bg-gradient-to-r from-red-50 to-white p-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-red-700">Global Emergency Stop</h2>
            <p className="text-sm text-ink-secondary">Cut all active relays / actuators for this tenant in one action.</p>
          </div>
          <button
            type="button"
            onClick={toggleEstop}
            className={`inline-flex items-center gap-2 rounded-2xl px-6 py-3 text-sm font-bold uppercase tracking-wide ${
              estop
                ? "bg-red-600 text-white ring-4 ring-red-200"
                : "border-2 border-red-500 bg-white text-red-600 hover:bg-red-50"
            }`}
          >
            <AlertOctagon className="h-5 w-5" />
            {estop ? "E-STOP ACTIVE" : "Activate E-STOP"}
          </button>
        </div>
      </CreamCard>

      <div className="grid gap-6 xl:grid-cols-2">
        <CreamCard className="p-5">
          <h2 className="text-lg font-semibold text-ink-primary">Actuator & relay controls</h2>
          <ul className="mt-4 space-y-3">
            {actuators.map((actuator) => {
              const on = Boolean(relayState[actuator.id]) && !estop;
              return (
                <li
                  key={actuator.id}
                  className="flex items-center justify-between gap-3 rounded-xl border border-cream-border bg-cream-alt px-4 py-3"
                >
                  <div>
                    <p className="font-medium text-ink-primary">{actuator.label}</p>
                    <p className="text-xs text-ink-secondary">{actuator.zone}</p>
                  </div>
                  <button
                    type="button"
                    disabled={estop}
                    onClick={() => toggleRelay(actuator.id)}
                    className={`relative h-8 w-14 rounded-full transition ${on ? "bg-accent-emerald" : "bg-cream-border"} ${
                      estop ? "opacity-40" : ""
                    }`}
                    aria-pressed={on}
                  >
                    <span
                      className={`absolute left-1 top-1 h-6 w-6 rounded-full bg-white shadow transition-transform duration-200 ${
                        on ? "translate-x-6" : "translate-x-0"
                      }`}
                    />
                  </button>
                </li>
              );
            })}
          </ul>
        </CreamCard>

        <CreamCard className="p-5">
          <h2 className="text-lg font-semibold text-ink-primary">Live telemetry charts</h2>
          <div className="mt-3 h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={series}>
                <CartesianGrid stroke="#ECECE8" strokeDasharray="4 4" />
                <XAxis dataKey="t" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="temp" name="Temp °C" stroke="#10B981" dot={false} strokeWidth={2} />
                <Line type="monotone" dataKey="ph" name="pH" stroke="#2563EB" dot={false} strokeWidth={2} />
                <Line type="monotone" dataKey="humidity" name="Humidity %" stroke="#F59E0B" dot={false} strokeWidth={2} />
                <Line type="monotone" dataKey="battery" name="Battery %" stroke="#7C3AED" dot={false} strokeWidth={2} />
                <Line type="monotone" dataKey="rssi" name="LoRa RSSI" stroke="#4F46E5" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CreamCard>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <CreamCard className="relative min-h-[280px] overflow-hidden p-5 lg:col-span-3">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-ink-primary">
            <MapPin className="h-5 w-5 text-accent-cobalt" />
            Active fleet map preview
          </h2>
          <div className="absolute inset-0 mt-14 bg-[linear-gradient(#ecece8_1px,transparent_1px),linear-gradient(90deg,#ecece8_1px,transparent_1px)] bg-[size:28px_28px]" />
          <div className="relative mt-6 h-52">
            {fleetMarkers.map((m, idx) => (
              <span
                key={m.id}
                className="absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center"
                style={{
                  left: `${18 + idx * 22}%`,
                  top: `${30 + (idx % 3) * 22}%`,
                }}
              >
                <span className="rounded-full bg-accent-indigo px-2 py-1 text-[10px] font-semibold text-white shadow">
                  {m.label}
                </span>
                <span className="mt-1 font-mono text-[10px] text-ink-secondary">
                  {m.lat.toFixed(3)}, {m.lon.toFixed(3)}
                </span>
              </span>
            ))}
          </div>
        </CreamCard>

        <CreamCard className="p-5 lg:col-span-2">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-ink-primary">
            <Radio className="h-5 w-5 text-accent-emerald" />
            Audit event stream
          </h2>
          <ul className="mt-4 max-h-64 space-y-2 overflow-y-auto">
            {audit.length === 0 ? (
              <li className="text-sm text-ink-secondary">Waiting for control / telemetry events…</li>
            ) : (
              audit.map((row) => (
                <li
                  key={row.id}
                  className={`rounded-lg border px-3 py-2 text-xs ${
                    row.level === "critical"
                      ? "border-red-200 bg-red-50 text-red-700"
                      : row.level === "warn"
                        ? "border-accent-amber/40 bg-accent-amber-soft/40 text-ink-primary"
                        : "border-cream-border bg-white text-ink-primary"
                  }`}
                >
                  <span className="font-mono text-[10px] text-ink-tertiary">{row.time}</span>
                  <p className="mt-0.5">{row.message}</p>
                </li>
              ))
            )}
          </ul>
        </CreamCard>
      </div>
    </HqPageContent>
  );
}
