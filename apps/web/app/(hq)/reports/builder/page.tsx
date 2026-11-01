"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
import { ReportBuilderCanvas } from "@/components/reports/ReportBuilderCanvas";
import { createReportTemplate } from "@/lib/api/reports";
import { Button } from "@/components/ui/button";

export default function ReportBuilderPage() {
  const router = useRouter();
  const [name, setName] = useState("Monthly ops report");
  const [sections, setSections] = useState<{ id: string; type: string; title: string }[]>([]);

  async function save() {
    const row = await createReportTemplate({
      name,
      description: "",
      config_json: { sections },
    });
    router.push(`/reports/${row.id}/schedule`);
  }

  return (
    <HqPageShell
      action={
        <Button type="button" onClick={() => void save()}>
          Save template
        </Button>
      }
    >
      <input
        className="mb-4 w-full max-w-md rounded-lg border border-border bg-card px-3 py-2 text-sm"
        value={name}
        onChange={(e) => setName(e.target.value)}
        aria-label="Report name"
      />
      <ReportBuilderCanvas onChange={setSections} />
    </HqPageShell>
  );
}
