import type { LucideIcon } from "lucide-react";
import {
  BarChart3,
  Cpu,
  Crosshair,
  Key,
  Layers,
  Map,
  QrCode,
  Radio,
  Settings,
  Tag,
  Workflow,
} from "lucide-react";

export type HqNavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
  accentClass: string;
  iconBgClass: string;
};

export type HqNavSection = {
  label?: string;
  items: HqNavItem[];
};

export const HQ_NAV_SECTIONS: HqNavSection[] = [
  {
    items: [
      {
        href: "/dashboard",
        label: "Dashboard",
        icon: BarChart3,
        accentClass: "text-accent-cobalt",
        iconBgClass: "bg-accent-cobalt-soft",
      },
      {
        href: "/control-center",
        label: "Control Center",
        icon: Crosshair,
        accentClass: "text-accent-emerald",
        iconBgClass: "bg-accent-emerald-soft",
      },
      {
        href: "/device-profiles",
        label: "Device Profiles",
        icon: Layers,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
      },
      {
        href: "/devices",
        label: "Devices",
        icon: Radio,
        accentClass: "text-accent-cobalt",
        iconBgClass: "bg-accent-cobalt-soft",
      },
      {
        href: "/claim-tokens",
        label: "Claim Tokens",
        icon: QrCode,
        accentClass: "text-accent-amber",
        iconBgClass: "bg-accent-amber-soft",
      },
    ],
  },
  {
    label: "Studio",
    items: [
      {
        href: "/studio/firmware",
        label: "Firmware Studio",
        icon: Cpu,
        accentClass: "text-accent-violet",
        iconBgClass: "bg-accent-violet-soft",
      },
      {
        href: "/studio/missions",
        label: "Mission Studio",
        icon: Map,
        accentClass: "text-accent-amber",
        iconBgClass: "bg-accent-amber-soft",
      },
      {
        href: "/studio/automation",
        label: "Automation Studio",
        icon: Workflow,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
      },
    ],
  },
  {
    items: [
      {
        href: "/developer/api-keys",
        label: "API Keys",
        icon: Key,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
      },
      {
        href: "/settings/tenant-branding",
        label: "White-Label",
        icon: Tag,
        accentClass: "text-accent-amber",
        iconBgClass: "bg-accent-amber-soft",
      },
      {
        href: "/settings",
        label: "Settings",
        icon: Settings,
        accentClass: "text-ink-secondary",
        iconBgClass: "bg-cream-muted",
      },
    ],
  },
];

/** @deprecated Use HQ_NAV_SECTIONS — flat list for title lookup */
export const HQ_NAV_ITEMS: HqNavItem[] = HQ_NAV_SECTIONS.flatMap((s) => s.items);

export const HQ_PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/control-center": "Control Center",
  "/device-profiles": "Device Profiles",
  "/devices": "Devices",
  "/claim-tokens": "Claim Tokens",
  "/studio/firmware": "Firmware Studio",
  "/studio/missions": "Mission Studio",
  "/studio/automation": "Automation Studio",
  "/developer/api-keys": "API Keys",
  "/settings/tenant-branding": "White-Label",
  "/settings": "Settings",
};

export function titleForPath(pathname: string): string {
  if (HQ_PAGE_TITLES[pathname]) return HQ_PAGE_TITLES[pathname];
  for (const [path, title] of Object.entries(HQ_PAGE_TITLES)) {
    if (pathname.startsWith(path)) return title;
  }
  return "Web HQ";
}
