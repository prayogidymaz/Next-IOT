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
  Tag,
  Users,
  Sprout,
  Workflow,
  Share2,
  MapPin,
  Leaf,
  Code2,
  Webhook,
  BookOpen,
  Store,
  FileBarChart,
  Sparkles,
  Boxes,
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
      {
        href: "/workflows/new",
        label: "Workflow builder",
        icon: Workflow,
        accentClass: "text-stone-700",
        iconBgClass: "bg-stone-100",
      },
      {
        href: "/workflows",
        label: "Workflow list",
        icon: Workflow,
        accentClass: "text-stone-700",
        iconBgClass: "bg-stone-100",
      },
      {
        href: "/marketplace",
        label: "Marketplace",
        icon: Layers,
        accentClass: "text-accent-emerald",
        iconBgClass: "bg-accent-emerald-soft",
      },
      {
        href: "/approval/pending",
        label: "Pending approvals",
        icon: FileText,
        accentClass: "text-accent-amber",
        iconBgClass: "bg-accent-amber-soft",
      },
    ],
  },
  {
    id: "fleet",
    label: "Fleet",
    collapsible: true,
    items: [
      {
        href: "/sites",
        label: "Sites",
        icon: MapPin,
        accentClass: "text-accent-emerald",
        iconBgClass: "bg-accent-emerald-soft",
      },
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
        href: "/fleet/templates",
        label: "Fleet Automation",
        icon: Boxes,
        accentClass: "text-accent-cobalt",
        iconBgClass: "bg-accent-cobalt-soft",
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
        href: "/analytics/workflows",
        label: "Workflow analytics",
        icon: Activity,
        accentClass: "text-accent-violet",
        iconBgClass: "bg-accent-violet-soft",
      },
      {
        href: "/analytics/yield",
        label: "Yield forecast",
        icon: Sprout,
        accentClass: "text-accent-emerald",
        iconBgClass: "bg-accent-emerald-soft",
      },
      {
        href: "/sustainability",
        label: "Sustainability",
        icon: Leaf,
        accentClass: "text-emerald-600",
        iconBgClass: "bg-emerald-500/10",
      },
      {
        href: "/reports",
        label: "Reports",
        icon: FileBarChart,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
      },
      {
        href: "/decisions",
        label: "AI Decisions",
        icon: Sparkles,
        accentClass: "text-accent-violet",
        iconBgClass: "bg-accent-violet-soft",
      },
      {
        href: "/mesh/graph",
        label: "Mesh Graph",
        icon: Share2,
        accentClass: "text-[#556B4A]",
        iconBgClass: "bg-[#F5EFE0]",
      },
    ],
  },
  {
    id: "developer",
    label: "Developer",
    collapsible: true,
    items: [
      {
        href: "/developer/docs",
        label: "API docs",
        icon: BookOpen,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
      },
      {
        href: "/developer/playground",
        label: "API playground",
        icon: Code2,
        accentClass: "text-accent-cobalt",
        iconBgClass: "bg-accent-cobalt-soft",
      },
      {
        href: "/developer/webhooks",
        label: "Webhooks",
        icon: Webhook,
        accentClass: "text-accent-violet",
        iconBgClass: "bg-accent-violet-soft",
      },
      {
        href: "/developer/api-keys",
        label: "API keys",
        icon: Key,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
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
        href: "/members",
        label: "Members & roles",
        icon: Users,
        accentClass: "text-accent-indigo",
        iconBgClass: "bg-accent-indigo-soft",
      },
      {
        href: "/approval/policy",
        label: "Approval policy",
        icon: FileText,
        accentClass: "text-accent-amber",
        iconBgClass: "bg-accent-amber-soft",
      },
      {
        href: "/sso",
        label: "Security & SSO",
        icon: Key,
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
        href: "/audit-log",
        label: "Audit Log",
        icon: FileText,
        accentClass: "text-ink-secondary",
        iconBgClass: "bg-cream-muted",
      },
    ],
  },
];

const SELLER_NAV_ITEM: HqNavItem = {
  href: "/marketplace/seller/dashboard",
  label: "Seller dashboard",
  icon: Store,
  accentClass: "text-accent-amber",
  iconBgClass: "bg-accent-amber-soft",
};

export function hqNavSectionsForRole(role: string | null, isSeller = false): HqNavSection[] {
  void role;
  if (!isSeller) return HQ_NAV_SECTIONS;
  return HQ_NAV_SECTIONS.map((section) =>
    section.id === "integration"
      ? { ...section, items: [...section.items, SELLER_NAV_ITEM] }
      : section,
  );
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
  "/mesh/graph": "Mesh Graph",
  "/workflows": "Workflows",
  "/workflows/new": "Workflow builder",
  "/marketplace": "Marketplace",
  "/approval/pending": "Pending approvals",
  "/approval/policy": "Approval policy",
  "/analytics/workflows": "Workflow analytics",
  "/analytics/yield": "Yield forecast",
  "/studio/missions": "Mission Studio",
  "/developer/api-keys": "API Keys",
  "/developer/docs": "API docs",
  "/developer/playground": "API playground",
  "/developer/webhooks": "Webhooks",
  "/sites": "Sites",
  "/sustainability": "Sustainability",
  "/marketplace/seller/dashboard": "Seller dashboard",
  "/marketplace/seller/payouts": "Seller payouts",
  "/settings/tenant-branding": "Tenant Settings",
  "/members": "Members & roles",
  "/audit-log": "Audit Log",
  "/profile": "My profile",
};

export function titleForPath(pathname: string): string {
  if (HQ_PAGE_TITLES[pathname]) return HQ_PAGE_TITLES[pathname];
  const sorted = Object.entries(HQ_PAGE_TITLES).sort((a, b) => b[0].length - a[0].length);
  for (const [path, title] of sorted) {
    if (pathname === path || pathname.startsWith(`${path}/`)) return title;
  }
  return "Web HQ";
}
