"use client";

import { useEffect, useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
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
    <HqPageShell>
      <WorkflowCanvas apiBase={API_BASE} token={token} />
    </HqPageShell>
  );
}
