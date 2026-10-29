"use client";

import { useEffect, useState } from "react";

import { fetchApprovalPolicy, updateApprovalPolicy } from "@/lib/api/workflowApproval";
import { useHqToast } from "@/hooks/useHqToast";

const ROLE_OPTIONS = ["tenant_admin", "operator", "viewer"] as const;

export function ApprovalPolicyPage() {
  const { showToast } = useHqToast();
  const [requireProduction, setRequireProduction] = useState(false);
  const [minApprovers, setMinApprovers] = useState(1);
  const [roles, setRoles] = useState<string[]>(["tenant_admin", "operator"]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void fetchApprovalPolicy()
      .then((p) => {
        setRequireProduction(p.require_approval_for_production);
        setMinApprovers(p.min_approvers);
        setRoles(p.approver_roles_json);
      })
      .catch((e: unknown) => showToast(e instanceof Error ? e.message : "Load failed", "error"));
  }, [showToast]);

  function toggleRole(role: string) {
    setRoles((prev) => (prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]));
  }

  async function save() {
    setSaving(true);
    try {
      await updateApprovalPolicy({
        require_approval_for_production: requireProduction,
        min_approvers: minApprovers,
        approver_roles_json: roles,
      });
      showToast("Policy saved", "success");
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Save failed", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-6 p-6">
      <h1 className="text-2xl font-semibold text-stone-900">Approval policy</h1>
      <p className="text-sm text-stone-600">Tenant admins only. Controls production workflow activation.</p>

      <label className="flex items-center gap-3 rounded-xl border border-stone-200 bg-white p-4">
        <input type="checkbox" checked={requireProduction} onChange={(e) => setRequireProduction(e.target.checked)} />
        <span className="text-sm font-medium text-stone-800">Require approval for production activation</span>
      </label>

      <label className="block text-sm text-stone-700">
        Minimum approvers
        <input
          type="number"
          min={1}
          max={5}
          className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2"
          value={minApprovers}
          onChange={(e) => setMinApprovers(Number(e.target.value))}
        />
      </label>

      <fieldset className="rounded-xl border border-stone-200 p-4">
        <legend className="px-1 text-sm font-medium text-stone-800">Approver roles</legend>
        <div className="mt-2 flex flex-wrap gap-2">
          {ROLE_OPTIONS.map((role) => (
            <button
              key={role}
              type="button"
              onClick={() => toggleRole(role)}
              className={`rounded-full px-3 py-1 text-xs ${
                roles.includes(role) ? "bg-stone-900 text-white" : "border border-stone-300 text-stone-700"
              }`}
            >
              {role}
            </button>
          ))}
        </div>
      </fieldset>

      <button
        type="button"
        disabled={saving}
        className="rounded-lg bg-stone-900 px-4 py-2 text-sm text-white disabled:opacity-50"
        onClick={() => void save()}
      >
        Save policy
      </button>
    </div>
  );
}
