"use client";

import { useEffect, useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
import { Button } from "@/components/ui/button";
import { createDeviceGroup, listDeviceGroups, type DeviceGroup } from "@/lib/api/fleet";

export default function FleetGroupsPage() {
  const [rows, setRows] = useState<DeviceGroup[]>([]);
  const [name, setName] = useState("North field");

  useEffect(() => {
    void listDeviceGroups().then(setRows).catch(() => setRows([]));
  }, []);

  return (
    <HqPageShell>
      <form
        className="mb-4 flex gap-2 text-sm"
        onSubmit={(e) => {
          e.preventDefault();
          void createDeviceGroup({ name, tag_filter_json: { region: "north" } }).then((g) => setRows((p) => [...p, g]));
        }}
      >
        <input className="rounded border border-border bg-card px-2 py-1" value={name} onChange={(e) => setName(e.target.value)} aria-label="Group name" />
        <Button type="submit" size="sm">
          Add group
        </Button>
      </form>
      <ul className="divide-y divide-border rounded-xl border border-border bg-card text-sm">
        {rows.map((g) => (
          <li key={g.id} className="px-4 py-3">
            {g.name}
          </li>
        ))}
      </ul>
    </HqPageShell>
  );
}
