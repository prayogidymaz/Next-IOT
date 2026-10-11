import { SuperAdminDashboard } from "@/components/super-admin/SuperAdminDashboard";
import { HqPageContent } from "@/components/hq/HqPageContent";

export default function SuperAdminDashboardPage() {
  return (
    <HqPageContent description="Platform-wide tenants, revenue, and health (super_admin only).">
      <SuperAdminDashboard />
    </HqPageContent>
  );
}
