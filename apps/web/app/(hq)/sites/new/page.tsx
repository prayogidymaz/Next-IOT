"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { createSite } from "@/lib/api/sites";
import { Button } from "@/components/ui/button";

export default function NewSitePage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [timezone, setTimezone] = useState("Asia/Jakarta");
  const [lat, setLat] = useState("-6.2");
  const [lng, setLng] = useState("106.8");

  async function submit() {
    const row = await createSite({
      name,
      slug: slug || name.toLowerCase().replace(/\s+/g, "-"),
      timezone,
      location_json: { lat: Number.parseFloat(lat), lng: Number.parseFloat(lng), address: name },
    });
    router.push(`/sites/${row.id}`);
  }

  return (
    <div className="container mx-auto max-w-lg space-y-3 px-4 py-6">
      <input className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm" placeholder="Site name" value={name} onChange={(e) => setName(e.target.value)} />
      <input className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm" placeholder="Slug" value={slug} onChange={(e) => setSlug(e.target.value)} />
      <input className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm" placeholder="Timezone" value={timezone} onChange={(e) => setTimezone(e.target.value)} />
      <div className="grid grid-cols-2 gap-2">
        <input className="rounded-lg border border-border bg-card px-3 py-2 text-sm" placeholder="Lat" value={lat} onChange={(e) => setLat(e.target.value)} />
        <input className="rounded-lg border border-border bg-card px-3 py-2 text-sm" placeholder="Lng" value={lng} onChange={(e) => setLng(e.target.value)} />
      </div>
      <Button type="button" onClick={() => void submit()}>
        Create site
      </Button>
    </div>
  );
}
