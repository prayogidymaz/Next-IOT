import { notFound } from "next/navigation";
import { NextIntlClientProvider } from "next-intl";

import { HqAppShell } from "@/components/hq/HqAppShell";
import { isAppLocale, loadMessages, type AppLocale } from "@/i18n";

export default async function LocaleHqLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale: raw } = await params;
  if (!isAppLocale(raw)) notFound();
  const locale: AppLocale = raw;
  const messages = await loadMessages(locale);
  return (
    <NextIntlClientProvider locale={locale} messages={messages}>
      <HqAppShell>{children}</HqAppShell>
    </NextIntlClientProvider>
  );
}
