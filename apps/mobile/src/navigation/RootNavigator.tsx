import { NavigationContainer } from "@react-navigation/native";
import { useEffect } from "react";

import { apiFetch, getStoredToken, setUnauthorizedHandler } from "@/lib/api/client";
import type { AuthUser } from "@/lib/api/endpoints";
import { useAuthStore } from "@/stores/authStore";

import { AuthStack } from "./AuthStack";
import { MainTabs } from "./MainTabs";

export function RootNavigator() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const setSession = useAuthStore((s) => s.setSession);
  const logout = useAuthStore((s) => s.logout);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      void logout();
    });
  }, [logout]);

  useEffect(() => {
    void (async () => {
      const token = await getStoredToken();
      if (!token) return;
      try {
        const res = await apiFetch("/api/v1/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
          auth: false,
        });
        if (!res.ok) return;
        const user = (await res.json()) as AuthUser;
        await setSession(token, user);
      } catch {
        /* ignore bootstrap errors */
      }
    })();
  }, [setSession]);

  return <NavigationContainer>{isAuthenticated ? <MainTabs /> : <AuthStack />}</NavigationContainer>;
}
