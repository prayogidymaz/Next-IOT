import type { Metadata } from "next";

import { CTASection } from "@/components/CTASection";
import { PricingTable } from "@/components/PricingTable";

export const metadata: Metadata = {
  title: "Pricing",
  description: "Paket Free, Starter, Pro, dan Enterprise untuk platform Next-IoT.",
};

export default function PricingPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
      <h1 className="text-4xl font-semibold text-slate-900">Pricing</h1>
      <p className="mt-3 max-w-2xl text-slate-600">
        Harga transparan dalam Rupiah. Upgrade kapan saja — billing terintegrasi Midtrans & Xendit.
      </p>
      <div className="mt-12">
        <PricingTable />
      </div>
      <CTASection />
    </div>
  );
}
