"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useState } from "react";

import { GlassAuthShell } from "@/components/auth/GlassAuthShell";
import { login } from "@/lib/auth/api";
import { setSessionTokens } from "@/lib/auth/session";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next") || "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await login(email.trim(), password);
      setSessionTokens(tokens.access_token, tokens.refresh_token);
      router.replace(nextPath.startsWith("/") ? nextPath : "/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <GlassAuthShell
      title="Sign in"
      subtitle="Access the Next-IoT control center with your enterprise credentials."
      footer={
        <>
          No account?{" "}
          <Link href="/register" className="font-medium text-accent-emerald hover:underline">
            Register workspace
          </Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={onSubmit}>
        <label className="block text-sm">
          <span className="text-ink-secondary">Email</span>
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1.5 w-full rounded-2xl border border-cream-border bg-white px-4 py-3 text-ink-primary outline-none ring-accent-cobalt/30 focus:ring-2"
          />
        </label>
        <label className="block text-sm">
          <span className="text-ink-secondary">Password</span>
          <input
            type="password"
            required
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1.5 w-full rounded-2xl border border-cream-border bg-white px-4 py-3 text-ink-primary outline-none ring-accent-cobalt/30 focus:ring-2"
          />
        </label>
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
        <button
          type="submit"
          disabled={loading}
          className="hq-btn-primary w-full py-3 disabled:opacity-60"
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </GlassAuthShell>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-cream-page" />}>
      <LoginForm />
    </Suspense>
  );
}
