import { AdminShell } from "@/components/AdminShell";
import { RateLimitsPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Rate limit monitor">
      <RateLimitsPanel />
    </AdminShell>
  );
}
