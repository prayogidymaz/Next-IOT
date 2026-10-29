"use client";

import { useParams } from "next/navigation";

import { MarketplaceDetailView } from "@/src/features/workflow-marketplace/MarketplaceDetailView";

export default function MarketplaceDetailRoute() {
  const params = useParams<{ id: string }>();
  return <MarketplaceDetailView templateId={params.id} />;
}
