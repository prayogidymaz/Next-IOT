"use client";

import { Shield } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useState } from "react";

import { login } from "@/lib/auth/api";
import { setSessionTokens } from "@/lib/auth/session";
import { roleFromAccessToken } from "@/lib/auth/token-role";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next") || "/dashboard";
  const errorParam = searchParams.get("error");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(
    errorParam === "super_admin_required" ? "Super admin credentials required for this console." : null,
  );
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await login(email.trim(), password);
      if (roleFromAccessToken(tokens.access_token) !== "super_admin") {
        setError("This console is restricted to super_admin operators.");
        return;
      }
      setSessionTokens(tokens.access_token, tokens.refresh_token);
      router.replace(nextPath.startsWith("/") ? nextPath : "/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-command-bg px-4">
      <div className="command-card w-full max-w-md p-8">
        <div className="mb-6 flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-command-accent-soft text-command-accent">
            <Shield className="h-6 w-6" />
          </span>
          <div>
            <h1 className="text-lg font-semibold tracking-tight">Next-IoT Command Center</h1>
            <p className="text-sm text-command-secondary">Super admin access only</p>
          </div>
        </div>
        <form className="space-y-4" onSubmit={onSubmit}>
          <label className="block text-sm">
            <span className="text-command-secondary">Email</span>
            <input
              type="email"
              required
              autoComplete="username"
              className="command-input mt-1 w-full"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
          <label className="block text-sm">
            <span className="text-command-secondary">Password</span>
            <input
              type="password"
              required
              autoComplete="current-password"
              className="command-input mt-1 w-full"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          {error ? <p className="text-sm text-red-400">{error}</p> : null}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-command-accent py-2.5 text-sm font-semibold text-command-bg transition hover:brightness-110 disabled:opacity-60"
          >
            {loading ? "Authenticating…" : "Enter command center"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function AdminLoginPage() {
  return (
    <Suspense fallback={<p className="p-8 text-sm text-command-secondary">Loading…</p>}>
      <LoginForm />
    </Suspense>
  );
}
