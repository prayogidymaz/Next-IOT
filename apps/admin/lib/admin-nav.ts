import type { LucideIcon } from "lucide-react";
import {
  Activity,
  BadgePercent,
  BarChart3,
  Bell,
  Building2,
  Database,
  Flag,
  Handshake,
  HeartPulse,
  LayoutDashboard,
  LineChart,
  Mail,
  MessageSquare,
  Radio,
  Receipt,
  ScrollText,
  Settings,
  Shield,
  Ticket,
  Timer,
  TrendingDown,
  UserSearch,
  Wallet,
} from "lucide-react";

export type AdminNavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
  shortcut?: string;
};

export type AdminNavGroup = {
  id: string;
  label: string;
  items: AdminNavItem[];
};

export const ADMIN_NAV_GROUPS: AdminNavGroup[] = [
  {
    id: "platform",
    label: "Platform operations",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      { href: "/tenants", label: "Tenants", icon: Building2, shortcut: "G T" },
      { href: "/billing", label: "Billing", icon: Receipt, shortcut: "G B" },
      { href: "/system", label: "System health", icon: Activity },
    ],
  },
  {
    id: "analytics",
    label: "Analytics & insights",
    items: [
      { href: "/analytics", label: "Analytics deep dive", icon: BarChart3 },
      { href: "/revenue-analytics", label: "Revenue analytics", icon: LineChart },
      { href: "/churn", label: "Churn analysis", icon: TrendingDown },
      { href: "/health-score", label: "Customer health score", icon: HeartPulse },
    ],
  },
  {
    id: "operations",
    label: "Operations",
    items: [
      { href: "/audit-log", label: "Audit log", icon: ScrollText },
      { href: "/system-logs", label: "System logs", icon: MessageSquare },
      { href: "/mqtt-monitor", label: "MQTT monitor", icon: Radio },
      { href: "/rate-limits", label: "Rate limit monitor", icon: Shield },
      { href: "/timeline", label: "Activity timeline", icon: Timer },
      { href: "/impersonation-audit", label: "Impersonation audit", icon: UserSearch },
    ],
  },
  {
    id: "communication",
    label: "Communication",
    items: [
      { href: "/announcements", label: "Announcements", icon: Bell, shortcut: "N A" },
      { href: "/email-templates", label: "Email templates", icon: Mail },
      { href: "/support-tickets", label: "Support tickets", icon: Ticket },
    ],
  },
  {
    id: "commercial",
    label: "Commercial",
    items: [
      { href: "/promo-codes", label: "Promo codes", icon: BadgePercent },
      { href: "/partners", label: "Partners", icon: Handshake },
      { href: "/finance", label: "Finance export", icon: Wallet },
    ],
  },
  {
    id: "settings",
    label: "Settings",
    items: [
      { href: "/settings", label: "Platform settings", icon: Settings },
      { href: "/feature-flags", label: "Feature flags", icon: Flag },
      { href: "/backup", label: "Backup / restore", icon: Database },
    ],
  },
];

export const ALL_NAV_ITEMS: AdminNavItem[] = ADMIN_NAV_GROUPS.flatMap((g) => g.items);
