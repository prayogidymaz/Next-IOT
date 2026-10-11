import type { DeviceResponse } from "@/lib/api/devices-schemas";

type DeviceStatusHeatmapProps = {
  devices: DeviceResponse[];
};

function cellClass(status: string): string {
  if (status === "online") return "bg-accent-emerald";
  if (status === "offline") return "bg-red-500";
  return "bg-accent-amber";
}

export function DeviceStatusHeatmap({ devices }: DeviceStatusHeatmapProps) {
  if (devices.length === 0) {
    return <p className="mt-3 text-sm text-ink-secondary">No devices registered yet.</p>;
  }
  return (
    <div className="mt-3 grid grid-cols-8 gap-1.5 sm:grid-cols-10">
      {devices.slice(0, 80).map((d) => (
        <div
          key={d.id}
          title={`${d.name} · ${d.status}`}
          className={`aspect-square rounded-sm ${cellClass(d.status)} opacity-90 transition hover:opacity-100`}
        />
      ))}
    </div>
  );
}
