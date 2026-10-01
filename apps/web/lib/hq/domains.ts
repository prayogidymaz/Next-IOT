export type HqDomainId =
  | "smart-home"
  | "smart-farming"
  | "cyberdeck"
  | "drone"
  | "robotics";

export type HqDomain = {
  id: HqDomainId;
  emoji: string;
  label: string;
  accent: "emerald" | "indigo" | "cobalt" | "amber" | "violet";
  softClass: string;
  iconClass: string;
};

export const HQ_DOMAINS: HqDomain[] = [
  {
    id: "smart-home",
    emoji: "🏠",
    label: "Smart Home",
    accent: "emerald",
    softClass: "bg-accent-emerald-soft text-accent-emerald",
    iconClass: "text-accent-emerald",
  },
  {
    id: "smart-farming",
    emoji: "🚜",
    label: "Smart Farming",
    accent: "emerald",
    softClass: "bg-accent-emerald-soft text-accent-emerald",
    iconClass: "text-accent-emerald",
  },
  {
    id: "cyberdeck",
    emoji: "📟",
    label: "Cyberdeck",
    accent: "indigo",
    softClass: "bg-accent-indigo-soft text-accent-indigo",
    iconClass: "text-accent-indigo",
  },
  {
    id: "drone",
    emoji: "🛸",
    label: "Drone",
    accent: "amber",
    softClass: "bg-accent-amber-soft text-accent-amber",
    iconClass: "text-accent-amber",
  },
  {
    id: "robotics",
    emoji: "🤖",
    label: "Robotics",
    accent: "violet",
    softClass: "bg-accent-violet-soft text-accent-violet",
    iconClass: "text-accent-violet",
  },
];

export function getDomain(id: HqDomainId): HqDomain {
  const match = HQ_DOMAINS.find((d) => d.id === id);
  if (match) return match;
  const fallback = HQ_DOMAINS[0];
  if (!fallback) throw new Error("HQ_DOMAINS must not be empty");
  return fallback;
}
