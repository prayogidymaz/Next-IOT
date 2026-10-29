"use client";

import { useCallback, useEffect, useState } from "react";

import { fetchApprovalPolicy, fetchPendingApprovals } from "@/lib/api/workflowApproval";

export type ActivationGuardState = {
  loading: boolean;
  canActivate: boolean;
  blockedReason: string | null;
  refresh: () => void;
};

/**
 * Mirrors server ApprovalService.can_activate when no dedicated status endpoint exists:
 * policy off → allowed; policy on → blocked unless no pending request (approved state requires backend check on enable).
 */
export function useCanActivateWorkflow(workflowId: string | undefined): ActivationGuardState {
  const [loading, setLoading] = useState(true);
  const [canActivate, setCanActivate] = useState(true);
  const [blockedReason, setBlockedReason] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!workflowId) {
      setLoading(false);
      setCanActivate(true);
      setBlockedReason(null);
      return;
    }
    setLoading(true);
    try {
      const policy = await fetchApprovalPolicy();
      if (!policy.require_approval_for_production) {
        setCanActivate(true);
        setBlockedReason(null);
        return;
      }
      const pending = await fetchPendingApprovals();
      const mine = pending.filter((p) => p.workflow_id === workflowId);
      if (mine.length > 0) {
        setCanActivate(false);
        setBlockedReason("An approval request is still pending review");
        return;
      }
      setCanActivate(false);
      setBlockedReason("Production activation requires an approved change request");
    } catch {
      setCanActivate(true);
      setBlockedReason(null);
    } finally {
      setLoading(false);
    }
  }, [workflowId]);

  useEffect(() => {
    void load();
  }, [load]);

  return { loading, canActivate, blockedReason, refresh: () => void load() };
}
