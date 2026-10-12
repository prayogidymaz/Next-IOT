import { AdminShell } from "@/components/AdminShell";
import { FeatureFlagsPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Feature flags">
      <FeatureFlagsPanel />
    </AdminShell>
  );
}
