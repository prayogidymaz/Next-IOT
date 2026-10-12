import { AdminShell } from "@/components/AdminShell";
import { MqttMonitorPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="MQTT monitor">
      <MqttMonitorPanel />
    </AdminShell>
  );
}
