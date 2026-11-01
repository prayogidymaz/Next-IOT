"use client";

import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { defaultLocale, isAppLocale, LOCALE_COOKIE, type AppLocale } from "@/i18n";
import idMessages from "@/messages/id.json";
import enMessages from "@/messages/en.json";
import zhMessages from "@/messages/zh-CN.json";

const MESSAGE_MAP: Record<AppLocale, Record<string, unknown>> = {
  id: idMessages,
  en: enMessages,
  "zh-CN": zhMessages,
};

function readLocale(): AppLocale {
  if (typeof window === "undefined") return defaultLocale;
  const stored = localStorage.getItem(LOCALE_COOKIE);
  if (stored && isAppLocale(stored)) return stored;
  return defaultLocale;
}

export function IntlAppProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<AppLocale>(defaultLocale);

  useEffect(() => {
    setLocale(readLocale());
    const onStorage = () => setLocale(readLocale());
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  return (
    <NextIntlClientProvider locale={locale} messages={MESSAGE_MAP[locale]}>
      {children}
    </NextIntlClientProvider>
  );
}
