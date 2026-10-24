"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { meshEventSchema, type MeshEventRecord } from "@/lib/api/mesh-schemas";
import { meshEventsStreamUrl } from "@/lib/api/mesh";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

const MAX_EVENTS = 200;

function parseSseChunk(buffer: string): { events: MeshEventRecord[]; rest: string } {
  const events: MeshEventRecord[] = [];
  const parts = buffer.split("\n\n");
  const rest = parts.pop() ?? "";
  for (const block of parts) {
    const lines = block.split("\n");
    let eventName = "";
    let dataLine = "";
    for (const line of lines) {
      if (line.startsWith("event:")) eventName = line.slice(6).trim();
      if (line.startsWith("data:")) dataLine = line.slice(5).trim();
    }
    if (eventName !== "mesh" || !dataLine) continue;
    try {
      const raw: unknown = JSON.parse(dataLine);
      events.push(meshEventSchema.parse(raw));
    } catch {
      /* skip malformed */
    }
  }
  return { events, rest };
}

export type MeshStreamState = "connecting" | "live" | "paused" | "offline";

export function useMeshEventStream(paused: boolean) {
  const [events, setEvents] = useState<MeshEventRecord[]>([]);
  const [state, setState] = useState<MeshStreamState>("connecting");
  const bufferRef = useRef("");
  const eventsPerMinRef = useRef(0);
  const windowStartRef = useRef(Date.now());
  const [eventsPerMin, setEventsPerMin] = useState(0);

  const pushEvents = useCallback(
    (incoming: MeshEventRecord[]) => {
      if (paused || incoming.length === 0) return;
      eventsPerMinRef.current += incoming.length;
      setEvents((prev) => [...incoming, ...prev].slice(0, MAX_EVENTS));
    },
    [paused],
  );

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token) {
      setState("offline");
      return;
    }

    let cancelled = false;
    const controller = new AbortController();

    const run = async () => {
      setState("connecting");
      try {
        const res = await fetch(meshEventsStreamUrl(), {
          headers: { Authorization: `Bearer ${token}`, Accept: "text/event-stream" },
          signal: controller.signal,
        });
        if (!res.ok || !res.body) {
          setState("offline");
          return;
        }
        setState("live");
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        while (!cancelled) {
          const { done, value } = await reader.read();
          if (done) break;
          bufferRef.current += decoder.decode(value, { stream: true });
          const parsed = parseSseChunk(bufferRef.current);
          bufferRef.current = parsed.rest;
          pushEvents(parsed.events);
        }
      } catch {
        if (!cancelled) setState("offline");
      }
    };

    void run();

    const interval = window.setInterval(() => {
      const elapsedMin = Math.max((Date.now() - windowStartRef.current) / 60000, 1 / 60);
      setEventsPerMin(Math.round(eventsPerMinRef.current / elapsedMin));
      eventsPerMinRef.current = 0;
      windowStartRef.current = Date.now();
    }, 5000);

    return () => {
      cancelled = true;
      controller.abort();
      window.clearInterval(interval);
    };
  }, [pushEvents]);

  return {
    events,
    state: paused && state !== "offline" ? "paused" : state,
    eventsPerMin,
    prepend: pushEvents,
  };
}
