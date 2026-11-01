"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

import type { SiteRecord } from "@/lib/api/sites";

const MapInner = dynamic(() => import("@/components/sites/SiteMapInner"), { ssr: false });

type Props = { sites: SiteRecord[] };

export function SiteMapView({ sites }: Props) {
  const markers = useMemo(
    () =>
      sites
        .map((s) => {
          const lat = s.location_json.lat;
          const lng = s.location_json.lng;
          if (typeof lat !== "number" || typeof lng !== "number") return null;
          return { id: s.id, name: s.name, lat, lng };
        })
        .filter((m): m is { id: string; name: string; lat: number; lng: number } => m !== null),
    [sites],
  );

  if (markers.length === 0) return null;
  return (
    <div className="h-64 overflow-hidden rounded-xl border border-border">
      <MapInner markers={markers} />
    </div>
  );
}
