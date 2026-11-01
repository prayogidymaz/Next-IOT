"use client";

import { useEffect, useState } from "react";

import { HqPageContent } from "@/components/hq/HqPageContent";
import { fetchAuthMe, type AuthUser } from "@/lib/auth/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";
import { Card, CardContent, CardHeader, CardTitle } from "@/src/components/ui/card";

export default function ProfilePage() {
  const [me, setMe] = useState<AuthUser | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token) return;
    void fetchAuthMe(token)
      .then(setMe)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load profile"));
  }, []);

  return (
    <HqPageContent>
      <Card>
        <CardHeader>
          <CardTitle>My profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {error ? <p className="text-red-600">{error}</p> : null}
          {me ? (
            <>
              <p>
                <span className="text-muted-foreground">Email:</span> {me.email}
              </p>
              <p>
                <span className="text-muted-foreground">Role:</span> {me.role}
              </p>
              <p>
                <span className="text-muted-foreground">Tenant:</span> {me.tenant_id}
              </p>
              <p>
                <span className="text-muted-foreground">Permissions:</span> {me.permissions.length ? me.permissions.join(", ") : "—"}
              </p>
            </>
          ) : (
            <p className="text-muted-foreground">{error ? null : "Loading…"}</p>
          )}
        </CardContent>
      </Card>
    </HqPageContent>
  );
}
