"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { GlassAuthShell } from "@/components/auth/GlassAuthShell";
import { register } from "@/lib/auth/api";
import { setSessionTokens } from "@/lib/auth/session";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [tenantName, setTenantName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const payload: { email: string; password: string; tenant_name?: string } = {
        email: email.trim(),
        password,
      };
      if (tenantName.trim()) payload.tenant_name = tenantName.trim();
      const { tokens } = await register(payload);
      setSessionTokens(tokens.access_token, tokens.refresh_token);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <GlassAuthShell
      title="Create workspace"
      subtitle="Register your tenant — a default organization is created automatically."
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-accent-cobalt hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={onSubmit}>
        <label className="block text-sm">
          <span className="text-ink-secondary">Work email</span>
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1.5 w-full rounded-2xl border border-cream-border bg-white px-4 py-3 text-ink-primary outline-none ring-accent-emerald/30 focus:ring-2"
          />
        </label>
        <label className="block text-sm">
          <span className="text-ink-secondary">Organization name (optional)</span>
          <input
            type="text"
            value={tenantName}
            onChange={(e) => setTenantName(e.target.value)}
            placeholder="Acme IoT Ops"
            className="mt-1.5 w-full rounded-2xl border border-cream-border bg-white px-4 py-3 text-ink-primary outline-none ring-accent-emerald/30 focus:ring-2"
          />
        </label>
        <label className="block text-sm">
          <span className="text-ink-secondary">Password</span>
          <input
            type="password"
            required
            minLength={8}
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1.5 w-full rounded-2xl border border-cream-border bg-white px-4 py-3 text-ink-primary outline-none ring-accent-emerald/30 focus:ring-2"
          />
        </label>
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-2xl bg-accent-emerald py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-60"
        >
          {loading ? "Creating…" : "Create workspace"}
        </button>
      </form>
    </GlassAuthShell>
  );
}
