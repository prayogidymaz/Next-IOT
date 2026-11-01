"use client";

import { useParams } from "next/navigation";

export default function ReportHistoryPage() {
  const params = useParams<{ id: string }>();
  return (
    <div className="container mx-auto px-4 py-6 text-sm text-muted-foreground">
      Generation history: GET /api/v1/reports/templates/{params.id}/history
    </div>
  );
}
