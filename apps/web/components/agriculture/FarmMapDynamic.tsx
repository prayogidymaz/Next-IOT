"use client";

import dynamic from "next/dynamic";

import type { FarmMapData } from "@/lib/agriculture/api";

const FarmMap = dynamic(() => import("./FarmMap").then((m) => m.FarmMap), { ssr: false });

export function FarmMapDynamic(props: { data: FarmMapData; farmId: string }) {
  return <FarmMap {...props} />;
}
