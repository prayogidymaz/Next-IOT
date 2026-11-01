import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { IntlAppProvider } from "@/components/i18n/IntlAppProvider";
import { ThemeProvider } from "@/src/components/ThemeProvider";

import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Next-IoT Web HQ",
  description: "Warm cream modern operator dashboard, studio tools, and white-label HQ",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="bg-background font-sans text-foreground">
        <ThemeProvider>
          <IntlAppProvider>{children}</IntlAppProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
