"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
import { Button } from "@/components/ui/button";
import { createConfigTemplate, listConfigTemplates, type DeviceConfigTemplate } from "@/lib/api/fleet";

export default function FleetTemplatesPage() {
  const [rows, setRows] = useState<DeviceConfigTemplate[]>([]);
  const [name, setName] = useState("Greenhouse default");
  const [deviceType, setDeviceType] = useState("sensor-node");

  useEffect(() => {
    void listConfigTemplates().then(setRows).catch(() => setRows([]));
  }, []);

  async function create() {
    const row = await createConfigTemplate({ name, device_type: deviceType, config_json: {}, firmware_version: "1.0.0" });
    setRows((prev) => [...prev, row]);
  }

  return (
    <HqPageShell
      action={
        <div className="flex gap-2 text-sm">
          <Link href="/fleet/provision" className="text-primary">
            Provision
          </Link>
          <Link href="/fleet/groups" className="text-primary">
            Groups
          </Link>
          <Link href="/fleet/sync" className="text-primary">
            Sync
          </Link>
        </div>
      }
    >
      <form
        className="mb-4 flex flex-wrap gap-2 text-sm"
        onSubmit={(e) => {
          e.preventDefault();
          void create();
        }}
      >
        <input className="rounded border border-border bg-card px-2 py-1" value={name} onChange={(e) => setName(e.target.value)} aria-label="Template name" />
        <input className="rounded border border-border bg-card px-2 py-1" value={deviceType} onChange={(e) => setDeviceType(e.target.value)} aria-label="Device type" />
        <Button type="submit" size="sm">
          Create template
        </Button>
      </form>
      <ul className="divide-y divide-border rounded-xl border border-border bg-card text-sm">
        {rows.map((t) => (
          <li key={t.id} className="px-4 py-3">
            {t.name} · {t.device_type} · FW {t.firmware_version}
          </li>
        ))}
      </ul>
    </HqPageShell>
  );
}
