"use client";

export function healthTone(status: string): "ok" | "warn" | "bad" | "unknown" {
  const s = status.toLowerCase();
  if (s === "ok" || s === "healthy") return "ok";
  if (s === "degraded" || s === "unknown") return "warn";
  if (s === "down" || s === "stopped" || s === "error") return "bad";
  return "unknown";
}

const DOT: Record<ReturnType<typeof healthTone>, string> = {
  ok: "bg-emerald-500",
  warn: "bg-amber-500",
  bad: "bg-red-500",
  unknown: "bg-ink-tertiary",
};

export function HealthDot({ status }: { status: string }) {
  const tone = healthTone(status);
  return <span className={`inline-block h-2.5 w-2.5 rounded-full ${DOT[tone]}`} aria-hidden />;
}
