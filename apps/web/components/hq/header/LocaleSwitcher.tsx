"use client";

import { LOCALE_COOKIE, type AppLocale, isAppLocale } from "@/i18n";

const OPTIONS: { value: AppLocale; label: string }[] = [
  { value: "id", label: "ID" },
  { value: "en", label: "EN" },
  { value: "zh-CN", label: "中文" },
];

export function LocaleSwitcher() {
  function onChange(value: string) {
    if (!isAppLocale(value)) return;
    localStorage.setItem(LOCALE_COOKIE, value);
    document.cookie = `${LOCALE_COOKIE}=${value}; path=/; max-age=31536000`;
    window.dispatchEvent(new Event("storage"));
    window.location.reload();
  }

  const current = typeof window !== "undefined" ? localStorage.getItem(LOCALE_COOKIE) : null;

  return (
    <select
      className="hidden rounded-lg border border-border bg-card px-2 py-1.5 text-xs text-foreground md:inline-block"
      aria-label="Language"
      defaultValue={current && isAppLocale(current) ? current : "id"}
      onChange={(e) => onChange(e.target.value)}
    >
      {OPTIONS.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}
