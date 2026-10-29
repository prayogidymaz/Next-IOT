"use client";

import { useEffect, useState } from "react";

import { WorkflowCanvas } from "@/src/features/workflow-builder/WorkflowCanvas";
import { getApiBaseUrl } from "@/lib/auth/api";
import { readApiAccessToken } from "@/lib/auth/api-headers";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? getApiBaseUrl();

export default function NewWorkflowPage() {
  const [token, setToken] = useState("");
  useEffect(() => {
    setToken(readApiAccessToken() ?? "");
  }, []);

  return (
    <div className="p-6">
      <h1 className="mb-4 text-2xl font-semibold text-stone-900">New workflow</h1>
      <WorkflowCanvas apiBase={API_BASE} token={token} />
    </div>
  );
}
