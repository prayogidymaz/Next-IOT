import { SuperAdminBillingPanel } from "@/components/super-admin/SuperAdminBillingPanel";
import { HqPageContent } from "@/components/hq/HqPageContent";

export default function SuperAdminBillingPage() {
  return (
    <HqPageContent description="Platform invoices, revenue, and billing cycle controls.">
      <SuperAdminBillingPanel />
    </HqPageContent>
  );
}
