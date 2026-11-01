import { defaultLocale, isAppLocale, LOCALE_COOKIE, type AppLocale } from "@/i18n";

/** Read persisted UI locale from cookie or localStorage (client only). */
export function readClientLocale(): AppLocale {
  if (typeof document === "undefined") return defaultLocale;
  const cookie = document.cookie
    .split(";")
    .map((p) => p.trim())
    .find((p) => p.startsWith(`${LOCALE_COOKIE}=`));
  const fromCookie = cookie?.split("=")[1];
  if (fromCookie && isAppLocale(fromCookie)) return fromCookie;
  const fromStorage = localStorage.getItem(LOCALE_COOKIE);
  if (fromStorage && isAppLocale(fromStorage)) return fromStorage;
  return defaultLocale;
}

/** Map next-intl locale to marketplace template locale field. */
export function marketplaceLocaleParam(locale: AppLocale): string {
  return locale;
}
