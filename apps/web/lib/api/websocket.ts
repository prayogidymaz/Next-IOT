import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";

export type TelemetryWsMessage =
  | {
      type: "telemetry.reading";
      device_id?: string;
      metrics?: Record<string, unknown>;
      recorded_at?: string;
      timestamp?: string;
    }
  | {
      type: "audit.control" | "audit.command";
      action?: string;
      actor?: string;
      details?: Record<string, unknown>;
      domain?: string;
      device_id?: string;
      command_type?: string;
      timestamp?: string;
    }
  | {
      type: "relay.toggle" | "emergency.stop";
      domain?: string;
      details?: Record<string, unknown>;
    }
  | { type: string; [key: string]: unknown };

function readAccessToken(): string | null {
  if (typeof document === "undefined") return null;
  const prefix = `${ACCESS_TOKEN_COOKIE}=`;
  const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(prefix));
  if (!match) return null;
  return decodeURIComponent(match.slice(prefix.length));
}

export function getTelemetryWebSocketUrl(): string | null {
  const token = readAccessToken();
  if (!token) return null;
  const httpBase = getApiBaseUrl().replace(/\/$/, "");
  const wsBase = httpBase.replace(/^http/i, "ws");
  return `${wsBase}/api/v1/ws/telemetry?token=${encodeURIComponent(token)}`;
}

export function sendTelemetrySocketMessage(socket: WebSocket, payload: Record<string, unknown>) {
  if (socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify(payload));
}
