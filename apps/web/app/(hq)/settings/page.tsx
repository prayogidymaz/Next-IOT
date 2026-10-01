import Link from "next/link";
import { Bell, Shield, SlidersHorizontal, Users } from "lucide-react";

import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";

export default function SettingsPage() {
  return (
    <HqPageContent description="Organization preferences, security, notifications, and team access.">
      <div className="grid gap-4 md:grid-cols-2">
        {[
          { icon: Users, label: "Members & roles", href: "/settings/tenant-branding", soft: "bg-accent-cobalt-soft", color: "text-accent-cobalt" },
          { icon: Shield, label: "Security & SSO", href: "/developer/api-keys", soft: "bg-accent-indigo-soft", color: "text-accent-indigo" },
          { icon: Bell, label: "Notifications", href: "/dashboard", soft: "bg-accent-amber-soft", color: "text-accent-amber" },
          { icon: SlidersHorizontal, label: "White-label branding", href: "/settings/tenant-branding", soft: "bg-accent-violet-soft", color: "text-accent-violet" },
        ].map((item) => (
          <Link key={item.label} href={item.href}>
            <CreamCard hover className="flex items-center gap-4 p-5">
              <span className={`rounded-xl p-3 ${item.soft}`}>
                <item.icon className={`h-5 w-5 ${item.color}`} />
              </span>
              <span className="font-medium text-ink-primary">{item.label}</span>
            </CreamCard>
          </Link>
        ))}
      </div>
    </HqPageContent>
  );
}
