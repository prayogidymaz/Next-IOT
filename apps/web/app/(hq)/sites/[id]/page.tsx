"use client";

import { useParams } from "next/navigation";

import { SiteDetailView } from "@/components/sites/SiteDetailView";

export default function SiteDetailPage() {
  const params = useParams<{ id: string }>();
  return <SiteDetailView siteId={params.id} />;
}
