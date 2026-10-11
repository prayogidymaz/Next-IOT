import { SuperAdminTenantsPanel } from "@/components/super-admin/SuperAdminTenantsPanel";
import { HqPageContent } from "@/components/hq/HqPageContent";

export default function SuperAdminTenantsPage() {
  return (
    <HqPageContent description="Manage all tenants, trials, and subscription plans.">
      <SuperAdminTenantsPanel />
    </HqPageContent>
  );
}
