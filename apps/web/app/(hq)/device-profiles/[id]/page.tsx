import { DeviceProfileDetailPage } from "@/components/device-profiles/DeviceProfileDetailPage";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function DeviceProfileDetailRoute({ params }: PageProps) {
  const { id } = await params;
  return <DeviceProfileDetailPage profileId={id} />;
}
