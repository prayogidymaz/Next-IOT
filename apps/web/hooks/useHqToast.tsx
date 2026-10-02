"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

type ToastState = {
  message: string;
  tone: "error" | "success" | "info";
};

type HqToastContextValue = {
  toast: ToastState | null;
  showToast: (message: string, tone?: ToastState["tone"]) => void;
  clearToast: () => void;
};

const HqToastContext = createContext<HqToastContextValue | null>(null);

export function HqToastProvider({ children }: { children: ReactNode }) {
  const [toast, setToast] = useState<ToastState | null>(null);

  const showToast = useCallback((message: string, tone: ToastState["tone"] = "info") => {
    setToast({ message, tone });
    window.setTimeout(() => setToast(null), 5000);
  }, []);

  const clearToast = useCallback(() => setToast(null), []);

  const value = useMemo(() => ({ toast, showToast, clearToast }), [toast, showToast, clearToast]);

  return (
    <HqToastContext.Provider value={value}>
      {children}
      {toast ? (
        <div
          className={`fixed bottom-6 right-6 z-50 max-w-md rounded-2xl border px-4 py-3 text-sm font-medium shadow-lg ${
            toast.tone === "error"
              ? "border-red-200 bg-red-50 text-red-800"
              : toast.tone === "success"
                ? "border-emerald-200 bg-accent-emerald-soft text-accent-emerald"
                : "border-cream-border bg-white text-ink-primary"
          }`}
          role="status"
        >
          {toast.message}
        </div>
      ) : null}
    </HqToastContext.Provider>
  );
}

export function useHqToast() {
  const ctx = useContext(HqToastContext);
  if (!ctx) throw new Error("useHqToast must be used within HqToastProvider");
  return ctx;
}
