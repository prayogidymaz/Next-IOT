import type { Metadata } from "next";

import { FeatureGrid } from "@/components/FeatureGrid";

export const metadata: Metadata = {
  title: "Features",
  description: "Thing Model, MQTT, Rule Engine, notifications, Firmware Studio, billing.",
};

export default function FeaturesPage() {
  return (
    <div>
      <div className="border-b border-slate-100 bg-slate-50 py-12">
        <h1 className="text-center text-4xl font-semibold">Features</h1>
      </div>
      <FeatureGrid />
    </div>
  );
}
