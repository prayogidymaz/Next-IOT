import { DeviceDetailPage } from "@/components/device-profiles/DevicesPages";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function DeviceDetailRoute({ params }: PageProps) {
  const { id } = await params;
  return <DeviceDetailPage deviceId={id} />;
}
