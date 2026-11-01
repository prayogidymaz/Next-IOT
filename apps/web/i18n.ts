export const locales = ["id", "en", "zh-CN"] as const;
export type AppLocale = (typeof locales)[number];
export const defaultLocale: AppLocale = "id";

export const LOCALE_COOKIE = "NEXT_LOCALE";

export function isAppLocale(value: string): value is AppLocale {
  return (locales as readonly string[]).includes(value);
}

export async function loadMessages(locale: AppLocale): Promise<Record<string, unknown>> {
  switch (locale) {
    case "en":
      return (await import("./messages/en.json")).default as Record<string, unknown>;
    case "zh-CN":
      return (await import("./messages/zh-CN.json")).default as Record<string, unknown>;
    default:
      return (await import("./messages/id.json")).default as Record<string, unknown>;
  }
}
