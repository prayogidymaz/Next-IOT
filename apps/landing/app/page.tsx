import { Card } from "@next-iot/ui";

import { FAQHomeSection } from "@/components/landing/FAQHomeSection";
import { FeaturesHomeSection } from "@/components/landing/FeaturesHomeSection";
import { FinalCTAHomeSection } from "@/components/landing/FinalCTAHomeSection";
import { HardwareKitsSection } from "@/components/landing/HardwareKitsSection";
import { HowItWorksSection } from "@/components/landing/HowItWorksSection";
import { PricingHomeSection } from "@/components/landing/PricingHomeSection";
import { ProblemSolutionSection } from "@/components/landing/ProblemSolutionSection";
import { TestimonialsHomeSection } from "@/components/landing/TestimonialsHomeSection";
import { TrustSection } from "@/components/landing/TrustSection";
import { HeroSection } from "@/components/HeroSection";

export default function LandingHomePage() {
  return (
    <>
      <HeroSection />
      <TrustSection />
      <ProblemSolutionSection />
      <FeaturesHomeSection />
      <HowItWorksSection />
      <section id="demo" className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-white">Product demo</h2>
        <Card
          className="mt-6 flex aspect-video items-center justify-center bg-slate-900 text-slate-300 dark:border-slate-700"
          shadow="md"
        >
          [Visual: screen recording — AI Copilot + workflow mesh — link platform.next-iot.id]
        </Card>
      </section>
      <PricingHomeSection />
      <HardwareKitsSection />
      <TestimonialsHomeSection />
      <FAQHomeSection />
      <FinalCTAHomeSection />
    </>
  );
}
