"use client";

import { useEffect, useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
import { Button } from "@/components/ui/button";
import { downloadProvisionCsv, listConfigTemplates, startBulkProvision, type DeviceConfigTemplate } from "@/lib/api/fleet";

export default function FleetProvisionPage() {
  const [templates, setTemplates] = useState<DeviceConfigTemplate[]>([]);
  const [templateId, setTemplateId] = useState("");
  const [count, setCount] = useState(10);
  const [jobId, setJobId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void listConfigTemplates().then((list) => {
      setTemplates(list);
      if (list[0]) setTemplateId(list[0].id);
    });
  }, []);

  async function runProvision() {
    setBusy(true);
    try {
      const res = await startBulkProvision({ template_id: templateId || undefined, device_count: count });
      setJobId(res.job_id);
    } finally {
      setBusy(false);
    }
  }

  async function downloadCsv() {
    if (!jobId) return;
    const blob = await downloadProvisionCsv(jobId);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `provision-${jobId}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <HqPageShell>
      <div className="max-w-md space-y-3 rounded-xl border border-border bg-card p-4 text-sm">
        <label className="block">
          Template
          <select className="mt-1 w-full rounded border border-border bg-background px-2 py-1" value={templateId} onChange={(e) => setTemplateId(e.target.value)}>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          Device count
          <input type="number" min={1} max={500} className="mt-1 w-full rounded border border-border bg-background px-2 py-1" value={count} onChange={(e) => setCount(Number(e.target.value))} />
        </label>
        <Button type="button" disabled={busy} onClick={() => void runProvision()}>
          Start bulk job
        </Button>
        {jobId ? (
          <Button type="button" variant="outline" onClick={() => void downloadCsv()}>
            Download token CSV
          </Button>
        ) : null}
      </div>
    </HqPageShell>
  );
}
