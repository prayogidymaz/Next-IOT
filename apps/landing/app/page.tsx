import { Card } from "@next-iot/ui";
import Link from "next/link";

import { CTASection } from "@/components/CTASection";
import { FeatureGrid } from "@/components/FeatureGrid";
import { HeroSection } from "@/components/HeroSection";
import { PricingTable } from "@/components/PricingTable";
import { UseCaseShowcase } from "@/components/UseCaseShowcase";

export default function LandingHomePage() {
  return (
    <>
      <HeroSection />
      <section className="border-b border-slate-100 py-10">
        <p className="text-center text-sm text-slate-500">Dipercaya oleh tim operasional IoT di Indonesia</p>
        <div className="mt-4 flex flex-wrap justify-center gap-8 opacity-60">
          {["AgriCo", "SkyFleet", "BuildTech", "FactoryOne"].map((name) => (
            <span key={name} className="text-sm font-semibold text-slate-400">{name}</span>
          ))}
        </div>
      </section>
      <FeatureGrid />
      <UseCaseShowcase />
      <section id="demo" className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <Card className="aspect-video flex items-center justify-center bg-slate-900 text-slate-300" shadow="md">
          Product demo video — coming soon
        </Card>
      </section>
      <section className="bg-slate-50 py-20">
        <div className="mx-auto max-w-6xl px-4 md:px-6">
          <div className="flex items-end justify-between gap-4">
            <h2 className="text-3xl font-semibold text-slate-900">Pricing</h2>
            <Link href="/pricing" className="text-sm font-medium text-sky-600 hover:underline">
              Detail lengkap →
            </Link>
          </div>
          <div className="mt-10">
            <PricingTable compact />
          </div>
        </div>
      </section>
      <section className="mx-auto max-w-6xl px-4 py-20 md:px-6">
        <h2 className="text-center text-2xl font-semibold">Apa kata customer</h2>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            { quote: "Deploy fleet sensor dalam hitungan hari, bukan bulan.", name: "Rina W.", role: "CTO, AgriCo" },
            { quote: "Rule engine dan notifikasi WA menghemat 2 shift operator.", name: "Budi S.", role: "Ops Lead" },
            { quote: "Firmware Studio game-changer untuk tim hardware kecil.", name: "Dewi K.", role: "Head of IoT" },
          ].map((t) => (
            <Card key={t.name} className="p-6" shadow="sm">
              <p className="text-sm text-slate-700">&ldquo;{t.quote}&rdquo;</p>
              <p className="mt-4 text-sm font-semibold">{t.name}</p>
              <p className="text-xs text-slate-500">{t.role}</p>
            </Card>
          ))}
        </div>
      </section>
      <CTASection />
    </>
  );
}
