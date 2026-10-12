"use client";

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

type AdminThemeContextValue = {
  dark: boolean;
  toggleDark: () => void;
};

const AdminThemeContext = createContext<AdminThemeContextValue | null>(null);

export function AdminThemeProvider({ children }: { children: ReactNode }) {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("admin_theme_dark");
    if (stored === "1") setDark(true);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("admin_theme_dark", dark ? "1" : "0");
  }, [dark]);

  const value = useMemo(
    () => ({
      dark,
      toggleDark: () => setDark((d) => !d),
    }),
    [dark],
  );

  return <AdminThemeContext.Provider value={value}>{children}</AdminThemeContext.Provider>;
}

export function useAdminTheme() {
  const ctx = useContext(AdminThemeContext);
  if (!ctx) throw new Error("useAdminTheme requires AdminThemeProvider");
  return ctx;
}
