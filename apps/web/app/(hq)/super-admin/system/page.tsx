import { SuperAdminSystemPanel } from "@/components/super-admin/SuperAdminSystemPanel";
import { HqPageContent } from "@/components/hq/HqPageContent";

export default function SuperAdminSystemPage() {
  return (
    <HqPageContent description="Service health and platform runtime indicators.">
      <SuperAdminSystemPanel />
    </HqPageContent>
  );
}
