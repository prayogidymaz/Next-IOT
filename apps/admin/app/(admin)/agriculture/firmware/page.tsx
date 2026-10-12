import { AdminShell } from "@/components/AdminShell";
import { AgriFirmwarePanel } from "@/components/console/AgriAdminPanels";

export default function Page() {
  return (
    <AdminShell title="Agri firmware fleet">
      <AgriFirmwarePanel />
    </AdminShell>
  );
}
