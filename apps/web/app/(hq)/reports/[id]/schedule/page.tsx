"use client";

import { useParams } from "next/navigation";

export default function ReportSchedulePage() {
  const params = useParams<{ id: string }>();
  return (
    <div className="container mx-auto max-w-lg space-y-3 px-4 py-6 text-sm">
      <p className="text-foreground">Schedule for template {params.id}</p>
      <p className="text-muted-foreground">POST /api/v1/reports/templates/{params.id}/schedules with cron, recipients, format.</p>
    </div>
  );
}
