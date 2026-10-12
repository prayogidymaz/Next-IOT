import type { LucideIcon } from "lucide-react";
import {
  Activity,
  BarChart3,
  Bell,
  Cpu,
  FileText,
  Key,
  Layers,
  Mail,
  QrCode,
  Radio,
  Receipt,
  Sparkles,
  Tag,
  Users,
  Sprout,
  Workflow,
} from "lucide-react";

export type HqNavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
  accentClass: string;
  iconBgClass: string;
  badgeKey?: "alarms";
  shortcut?: string;
};

export type HqNavSection = {
  id: string;
  label: string;
  collapsible?: boolean;
  items: HqNavItem[];
};

export const HQ_NAV_SECTIONS: HqNavSection[] = [
  {
    id: "command",
    label: "Command",
    collapsible: true,
    items: [
      {
        href: "/dashboard",
        label: "Dashboard",
        icon: BarChart3,
        accentClass: "text-accent-cobalt",
        iconBgClass: "bg-accent-cobalt-soft",
        shortcut: "G D",
      },
      {
        href: "/alarms",
        label: "Alarms",
        icon: Bell,
        accentClass: "text-red-600",
        iconBgClass: "bg-red-50",
        badgeKey: "alarms",
        shortcut: "G A",
      },
      {
        href: "/studio/automation",
        label: "Automations",
        icon: Workflow,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
      },
    ],
  },
  {
    id: "fleet",
    label: "Fleet",
    collapsible: true,
    items: [
      {
        href: "/devices",
        label: "Devices",
        icon: Radio,
        accentClass: "text-accent-cobalt",
        iconBgClass: "bg-accent-cobalt-soft",
        shortcut: "G F",
      },
      {
        href: "/device-profiles",
        label: "Device Profiles",
        icon: Layers,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
      },
      {
        href: "/firmware-studio",
        label: "Firmware Studio",
        icon: Cpu,
        accentClass: "text-accent-violet",
        iconBgClass: "bg-accent-violet-soft",
      },
      {
        href: "/firmware-releases",
        label: "Firmware Releases",
        icon: Cpu,
        accentClass: "text-accent-emerald",
        iconBgClass: "bg-accent-emerald-soft",
      },
      {
        href: "/claim-tokens",
        label: "Claim Tokens",
        icon: QrCode,
        accentClass: "text-accent-amber",
        iconBgClass: "bg-accent-amber-soft",
      },
      {
        href: "/agriculture",
        label: "Smart Agriculture",
        icon: Sprout,
        accentClass: "text-accent-emerald",
        iconBgClass: "bg-accent-emerald-soft",
      },
    ],
  },
  {
    id: "intelligence",
    label: "Intelligence",
    collapsible: true,
    items: [
      {
        href: "/dashboard",
        label: "Analytics",
        icon: Activity,
        accentClass: "text-accent-violet",
        iconBgClass: "bg-accent-violet-soft",
      },
      {
        href: "/billing",
        label: "Reports",
        icon: FileText,
        accentClass: "text-accent-cobalt",
        iconBgClass: "bg-accent-cobalt-soft",
      },
      {
        href: "/dashboard",
        label: "AI Insights",
        icon: Sparkles,
        accentClass: "text-accent-amber",
        iconBgClass: "bg-accent-amber-soft",
      },
    ],
  },
  {
    id: "integration",
    label: "Integration",
    collapsible: true,
    items: [
      {
        href: "/notification-settings",
        label: "Notifications",
        icon: Mail,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
      },
      {
        href: "/devices",
        label: "MQTT Credentials",
        icon: Key,
        accentClass: "text-accent-cobalt",
        iconBgClass: "bg-accent-cobalt-soft",
      },
      {
        href: "/developer/api-keys",
        label: "API Keys",
        icon: Key,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
      },
    ],
  },
  {
    id: "settings",
    label: "Settings",
    collapsible: true,
    items: [
      {
        href: "/billing",
        label: "Billing",
        icon: Receipt,
        accentClass: "text-accent-emerald",
        iconBgClass: "bg-accent-emerald-soft",
      },
      {
        href: "/settings",
        label: "Users & Permissions",
        icon: Users,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
      },
      {
        href: "/settings/tenant-branding",
        label: "Tenant Settings",
        icon: Tag,
        accentClass: "text-accent-amber",
        iconBgClass: "bg-accent-amber-soft",
      },
      {
        href: "/settings",
        label: "Audit Log",
        icon: FileText,
        accentClass: "text-ink-secondary",
        iconBgClass: "bg-cream-muted",
      },
    ],
  },
];

export function hqNavSectionsForRole(role: string | null): HqNavSection[] {
  void role;
  return HQ_NAV_SECTIONS;
}

export const HQ_NAV_ITEMS: HqNavItem[] = HQ_NAV_SECTIONS.flatMap((s) => s.items);

export const HQ_PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/control-center": "Control Center",
  "/device-profiles": "Device Profiles",
  "/devices": "Devices",
  "/alarms": "Alarms",
  "/notification-settings": "Notification Settings",
  "/claim-tokens": "Claim Tokens",
  "/firmware-studio": "Firmware Studio",
  "/firmware-releases": "Firmware Releases",
  "/billing": "Billing",
  "/pricing": "Pricing",
  "/studio/automation": "Automations",
  "/studio/missions": "Mission Studio",
  "/developer/api-keys": "API Keys",
  "/settings/tenant-branding": "Tenant Settings",
  "/settings": "Settings",
};

export function titleForPath(pathname: string): string {
  if (HQ_PAGE_TITLES[pathname]) return HQ_PAGE_TITLES[pathname];
  for (const [path, title] of Object.entries(HQ_PAGE_TITLES)) {
    if (pathname.startsWith(path)) return title;
  }
  return "Web HQ";
}
