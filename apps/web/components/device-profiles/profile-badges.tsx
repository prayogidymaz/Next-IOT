import type { ProfileDomain, ProfileStatus } from "@/lib/api/device-profiles-schemas";

const DOMAIN_LABELS: Record<ProfileDomain, string> = {
  smart_home: "Smart Home",
  smart_farming: "Smart Farming",
  cyberdeck: "Cyberdeck",
  drone: "Drone",
  robotics: "Robotics",
  industrial: "Industrial",
  generic: "Generic",
};

const STATUS_STYLES: Record<ProfileStatus, string> = {
  draft: "bg-accent-amber-soft text-accent-amber",
  published: "bg-accent-emerald-soft text-accent-emerald",
  archived: "bg-cream-muted text-ink-secondary",
};

export function domainLabel(domain: ProfileDomain): string {
  return DOMAIN_LABELS[domain];
}

export function ProfileDomainBadge({ domain }: { domain: ProfileDomain }) {
  return (
    <span className="rounded-full bg-accent-cobalt-soft px-2 py-0.5 text-xs font-medium text-accent-cobalt">
      {domainLabel(domain)}
    </span>
  );
}

export function ProfileStatusBadge({ status }: { status: ProfileStatus }) {
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-semibold uppercase ${STATUS_STYLES[status]}`}>
      {status}
    </span>
  );
}

export const PROFILE_DOMAINS: ProfileDomain[] = [
  "smart_home",
  "smart_farming",
  "cyberdeck",
  "drone",
  "robotics",
  "industrial",
  "generic",
];
