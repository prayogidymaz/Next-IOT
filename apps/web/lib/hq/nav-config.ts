import type { LucideIcon } from "lucide-react";
import {
  Activity,
  BarChart3,
  Building2,
  Bell,
  Cpu,
  Crosshair,
  Key,
  Layers,
  Mail,
  Map,
  QrCode,
  Radio,
  Receipt,
  Settings,
  Shield,
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
        href: "/alarms",
        label: "Alarms",
        icon: Bell,
        accentClass: "text-red-600",
        iconBgClass: "bg-red-50",
      },
      {
        href: "/notification-settings",
        label: "Notifications",
        icon: Mail,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
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
        href: "/billing",
        label: "Billing",
        icon: Tag,
        accentClass: "text-accent-emerald",
        iconBgClass: "bg-accent-emerald-soft",
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

export const SUPER_ADMIN_NAV_SECTION: HqNavSection = {
  label: "Super Admin",
  items: [
    {
      href: "/super-admin/dashboard",
      label: "Dashboard",
      icon: Shield,
      accentClass: "text-accent-cobalt",
      iconBgClass: "bg-accent-cobalt-soft",
    },
    {
      href: "/super-admin/tenants",
      label: "Tenants",
      icon: Building2,
      accentClass: "text-accent-indigo",
      iconBgClass: "bg-accent-indigo-soft",
    },
    {
      href: "/super-admin/billing",
      label: "Billing",
      icon: Receipt,
      accentClass: "text-accent-emerald",
      iconBgClass: "bg-accent-emerald-soft",
    },
    {
      href: "/super-admin/system",
      label: "System Health",
      icon: Activity,
      accentClass: "text-accent-amber",
      iconBgClass: "bg-accent-amber-soft",
    },
  ],
};

export function hqNavSectionsForRole(role: string | null): HqNavSection[] {
  if (role === "super_admin") {
    return [...HQ_NAV_SECTIONS, SUPER_ADMIN_NAV_SECTION];
  }
  return HQ_NAV_SECTIONS;
}

/** @deprecated Use HQ_NAV_SECTIONS — flat list for title lookup */
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
  "/super-admin/dashboard": "Super Admin Dashboard",
  "/super-admin/tenants": "Super Admin — Tenants",
  "/super-admin/billing": "Super Admin — Billing",
  "/super-admin/system": "Super Admin — System",
  "/pricing": "Pricing",
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
