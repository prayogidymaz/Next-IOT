import { AdminShell } from "@/components/AdminShell";
import { PartnerDetailPanel } from "@/components/console/Step9CAdminPanels";

type Props = { params: Promise<{ id: string }> };

export default async function Page({ params }: Props) {
  const { id } = await params;
  return (
    <AdminShell title="Partner">
      <PartnerDetailPanel partnerId={id} />
    </AdminShell>
  );
}
