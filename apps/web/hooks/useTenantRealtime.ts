"use client";

import { useEffect, useRef, useState } from "react";

import { getApiBaseUrl } from "@/lib/auth/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

export type RealtimeConnectionState = "connecting" | "connected" | "degraded" | "offline";

type UseTenantRealtimeResult = {
  connection: RealtimeConnectionState;
  messagesPerMin: number;
  lastEventAt: number | null;
};

export function useTenantRealtime(): UseTenantRealtimeResult {
  const [connection, setConnection] = useState<RealtimeConnectionState>("connecting");
  const [messagesPerMin, setMessagesPerMin] = useState(0);
  const [lastEventAt, setLastEventAt] = useState<number | null>(null);
  const windowCountRef = useRef(0);
  const windowStartRef = useRef(Date.now());

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token) {
      setConnection("offline");
      return;
    }

    const base = getApiBaseUrl().replace(/\/$/, "");
    const url = `${base}/api/v1/realtime/stream?token=${encodeURIComponent(token)}&channels=telemetry,alarms,device_status,rule_executions`;
    const source = new EventSource(url);

    source.addEventListener("connected", () => setConnection("connected"));
    source.addEventListener("heartbeat", () => setConnection("connected"));
    const bump = () => {
      windowCountRef.current += 1;
      setLastEventAt(Date.now());
      setConnection("connected");
    };
    source.addEventListener("telemetry", bump);
    source.addEventListener("alarms", bump);
    source.addEventListener("device_status", bump);
    source.addEventListener("rule_executions", bump);
    source.onerror = () => setConnection("degraded");

    const interval = window.setInterval(() => {
      const now = Date.now();
      const elapsedMin = Math.max((now - windowStartRef.current) / 60000, 1 / 60);
      setMessagesPerMin(Math.round(windowCountRef.current / elapsedMin));
      windowCountRef.current = 0;
      windowStartRef.current = now;
    }, 5000);

    return () => {
      window.clearInterval(interval);
      source.close();
    };
  }, []);

  return { connection, messagesPerMin, lastEventAt };
}
