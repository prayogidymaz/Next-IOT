type AlarmSeverityBadgeProps = {
  severity: string;
};

const STYLES: Record<string, string> = {
  critical: "bg-red-100 text-red-800",
  major: "bg-orange-100 text-orange-800",
  minor: "bg-amber-100 text-amber-800",
  warning: "bg-yellow-100 text-yellow-800",
  info: "bg-sky-100 text-sky-800",
};

export function AlarmSeverityBadge({ severity }: AlarmSeverityBadgeProps) {
  const key = severity.toLowerCase();
  const cls = STYLES[key] ?? "bg-cream-muted text-ink-secondary";
  return (
    <span className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${cls}`}>
      {severity}
    </span>
  );
}
