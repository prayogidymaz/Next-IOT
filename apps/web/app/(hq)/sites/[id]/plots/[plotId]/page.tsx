"use client";

import { useParams } from "next/navigation";

import { PlotDetailView } from "@/components/sites/PlotDetailView";

export default function PlotDetailPage() {
  const params = useParams<{ id: string; plotId: string }>();
  return <PlotDetailView siteId={params.id} plotId={params.plotId} />;
}
