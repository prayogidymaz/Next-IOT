import { AdminShell } from "@/components/AdminShell";
import { PromoCodesPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Promo codes">
      <PromoCodesPanel />
    </AdminShell>
  );
}
