import { create } from "zustand";

import { clearStoredToken, setStoredToken } from "@/lib/api/client";
import { login as apiLogin, type AuthUser } from "@/lib/api/endpoints";

type AuthState = {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setSession: (token: string, user: AuthUser) => Promise<void>;
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  async login(email, password) {
    const { access_token, user } = await apiLogin(email, password);
    await setStoredToken(access_token);
    set({ token: access_token, user, isAuthenticated: true });
  },
  async logout() {
    await clearStoredToken();
    set({ token: null, user: null, isAuthenticated: false });
  },
  async setSession(token, user) {
    await setStoredToken(token);
    set({ token, user, isAuthenticated: true });
  },
}));
