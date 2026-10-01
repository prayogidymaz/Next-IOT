"use client";

import { useCallback, useEffect, useRef, useState, type MutableRefObject } from "react";

import {
  getTelemetryWebSocketUrl,
  sendTelemetrySocketMessage,
  type TelemetryWsMessage,
} from "@/lib/api/websocket";
import type { HqDomainId } from "@/lib/hq/domains";

export type TelemetryPoint = {
  t: string;
  temp: number;
  ph: number;
  humidity: number;
  battery: number;
  rssi: number;
};

export type AuditEvent = {
  id: string;
  time: string;
  message: string;
  level: "info" | "warn" | "critical";
};

/** Remote WS events → same React setters as the Control Center UI (optimistic + echo sync). */
export type ControlCenterRemoteSync = {
  applyRelayToggle: (relayId: string, on: boolean) => void;
  applyEmergencyStop: () => void;
};

const MAX_POINTS = 40;

function num(value: unknown, fallback: number): number {
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function seedPoint(): TelemetryPoint {
  const now = new Date();
  return {
    t: now.toLocaleTimeString(),
    temp: 28 + Math.random() * 4,
    ph: 7 + Math.random() * 0.6,
    humidity: 55 + Math.random() * 15,
    battery: 68 + Math.random() * 20,
    rssi: -58 - Math.random() * 18,
  };
}

function relayOnFromDetails(details: Record<string, unknown> | undefined): boolean | null {
  const raw = details?.state;
  if (raw === "ON" || raw === true) return true;
  if (raw === "OFF" || raw === false) return false;
  return null;
}

export function useControlCenterStream(
  domain: HqDomainId,
  remoteSyncRef: MutableRefObject<ControlCenterRemoteSync | null>,
) {
  const [connected, setConnected] = useState(false);
  const [series, setSeries] = useState<TelemetryPoint[]>(() =>
    Array.from({ length: 12 }, () => seedPoint()),
  );
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [fleet, setFleet] = useState<{ id: string; lat: number; lon: number }[]>([]);
  const socketRef = useRef<WebSocket | null>(null);
  const domainRef = useRef(domain);

  useEffect(() => {
    domainRef.current = domain;
  }, [domain]);

  const pushAudit = useCallback((message: string, level: AuditEvent["level"] = "info") => {
    setAudit((prev) =>
      [
        {
          id: crypto.randomUUID(),
          time: new Date().toLocaleTimeString(),
          message,
          level,
        },
        ...prev,
      ].slice(0, 30),
    );
  }, []);

  const applyRelayFromWs = useCallback((relayId: string, on: boolean) => {
    if (!relayId) return;
    remoteSyncRef.current?.applyRelayToggle(relayId, on);
  }, [remoteSyncRef]);

  const applyEstopFromWs = useCallback(() => {
    remoteSyncRef.current?.applyEmergencyStop();
  }, [remoteSyncRef]);

  const applyControlMessage = useCallback(
    (msg: TelemetryWsMessage) => {
      if (msg.type !== "audit.control") return;
      const action = msg.action;
      const details = (msg.details ?? {}) as Record<string, unknown>;

      if (action === "emergency.stop") {
        applyEstopFromWs();
        return;
      }
      if (action === "relay.toggle") {
        const relayId = String(details.relay_id ?? "");
        const on = relayOnFromDetails(details);
        if (relayId && on !== null) applyRelayFromWs(relayId, on);
      }
    },
    [applyEstopFromWs, applyRelayFromWs],
  );

  const applyTelemetry = useCallback((metrics: Record<string, unknown>) => {
    setSeries((prev) => {
      const next = [
        ...prev,
        {
          t: new Date().toLocaleTimeString(),
          temp: num(metrics.temperature ?? metrics.temp, prev.at(-1)?.temp ?? 30),
          ph: num(metrics.ph ?? metrics.pH, prev.at(-1)?.ph ?? 7.2),
          humidity: num(metrics.humidity, prev.at(-1)?.humidity ?? 60),
          battery: num(metrics.battery ?? metrics.battery_pct, prev.at(-1)?.battery ?? 75),
          rssi: num(metrics.rssi ?? metrics.lora_rssi, prev.at(-1)?.rssi ?? -65),
        },
      ];
      return next.slice(-MAX_POINTS);
    });
    const lat = num(metrics.lat ?? metrics.latitude, NaN);
    const lon = num(metrics.lon ?? metrics.longitude, NaN);
    if (Number.isFinite(lat) && Number.isFinite(lon)) {
      setFleet((prev) => {
        const id = String(metrics.device_id ?? "asset");
        const rest = prev.filter((p) => p.id !== id);
        return [...rest, { id, lat, lon }].slice(-12);
      });
    }
  }, []);

  useEffect(() => {
    const url = getTelemetryWebSocketUrl();
    if (!url) {
      pushAudit("WebSocket offline — sign in required for live stream.", "warn");
      return;
    }

    const socket = new WebSocket(url);
    socketRef.current = socket;

    socket.onopen = () => {
      setConnected(true);
      pushAudit("Telemetry stream connected.", "info");
    };
    socket.onclose = () => {
      setConnected(false);
      pushAudit("Telemetry stream disconnected.", "warn");
    };
    socket.onmessage = (evt) => {
      try {
        const msg = JSON.parse(String(evt.data)) as TelemetryWsMessage;
        if (msg.type === "telemetry.reading" && msg.metrics) {
          applyTelemetry({ ...msg.metrics, device_id: msg.device_id });
          return;
        }
        if (msg.type === "audit.control") {
          applyControlMessage(msg);
          pushAudit(
            `${msg.actor ?? "operator"} · ${msg.action ?? "control"} ${JSON.stringify(msg.details ?? {})}`,
            msg.action === "emergency.stop" ? "critical" : "info",
          );
          return;
        }
        if (msg.type === "relay.toggle") {
          const details = (msg.details ?? {}) as Record<string, unknown>;
          const relayId = String(details.relay_id ?? "");
          const on = relayOnFromDetails(details);
          if (relayId && on !== null) applyRelayFromWs(relayId, on);
          return;
        }
        if (msg.type === "emergency.stop") {
          applyEstopFromWs();
          return;
        }
        if (msg.type === "audit.command") {
          pushAudit(
            `Command ${msg.command_type ?? "dispatch"} → device ${String(msg.device_id ?? "").slice(0, 8)}`,
            "info",
          );
        }
      } catch {
        /* ignore malformed frames */
      }
    };

    return () => {
      socket.close();
      socketRef.current = null;
    };
  }, [applyControlMessage, applyEstopFromWs, applyRelayFromWs, applyTelemetry, pushAudit]);

  const publishRelayToggle = useCallback(
    (relayId: string, on: boolean) => {
      pushAudit(`Relay ${relayId} → ${on ? "ON" : "OFF"}`, "info");
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        sendTelemetrySocketMessage(socketRef.current, {
          type: "relay.toggle",
          domain: domainRef.current,
          details: { relay_id: relayId, state: on ? "ON" : "OFF" },
        });
      }
    },
    [pushAudit],
  );

  const publishEmergencyStop = useCallback(() => {
    pushAudit("GLOBAL EMERGENCY STOP activated — all actuators forced OFF.", "critical");
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      sendTelemetrySocketMessage(socketRef.current, {
        type: "emergency.stop",
        domain: domainRef.current,
        details: { scope: "tenant", actuators: "all" },
      });
    }
  }, [pushAudit]);

  return {
    connected,
    series,
    audit,
    fleet,
    publishRelayToggle,
    publishEmergencyStop,
    pushAudit,
  };
}
