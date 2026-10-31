import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { AnalyticsPlaceholder } from "@/components/landing/AnalyticsPlaceholder";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { SITE_URL } from "@/lib/site";

import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Next-IoT — Platform IoT Terbuka untuk Pertanian Modern Indonesia",
    template: "%s | Next-IoT",
  },
  description:
    "AI Copilot Bahasa Indonesia, visual workflow builder, universal device mesh, dan 6 hardware kit siap pakai. Trial gratis 14 hari.",
  openGraph: {
    type: "website",
    locale: "id_ID",
    siteName: "Next-IoT",
    title: "Next-IoT — Pertanian Modern Indonesia",
    description: "Setup dalam 1 hari. Hemat operational cost dengan automasi IoT terintegrasi.",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "Next-IoT Platform" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Next-IoT",
    description: "Platform IoT terbuka untuk smart farming Indonesia.",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" className={inter.variable} suppressHydrationWarning>
      <head>
        <AnalyticsPlaceholder />
      </head>
      <body className="font-sans bg-white text-slate-900 dark:bg-slate-950 dark:text-slate-100">
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
