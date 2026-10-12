import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { SITE_URL } from "@/lib/site";

import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Next-IoT — Platform IoT Komersial Indonesia",
    template: "%s | Next-IoT",
  },
  description:
    "Platform IoT end-to-end untuk Smart Farming, Drone/SAR, dan Industri 4.0. Thing Model, MQTT, Rule Engine, Firmware Studio — production-ready.",
  openGraph: {
    type: "website",
    locale: "id_ID",
    siteName: "Next-IoT",
    title: "Next-IoT — Platform IoT Komersial Indonesia",
    description: "Dari sensor sampai dashboard — semua terintegrasi dalam satu platform.",
  },
  twitter: {
    card: "summary_large_image",
    title: "Next-IoT",
    description: "Platform IoT komersial Indonesia — production-ready.",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" className={inter.variable}>
      <body className="font-sans">
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
