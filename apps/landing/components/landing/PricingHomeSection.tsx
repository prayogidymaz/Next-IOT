import Link from "next/link";

import { APP_URL } from "@/lib/site";
import { PRICING_TIERS } from "@/lib/landing-content";

export function PricingHomeSection() {
  return (
    <section id="pricing" className="bg-slate-50 py-20 dark:bg-slate-900/40">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-center text-3xl font-semibold text-slate-900 dark:text-white">Pricing</h2>
        <div className="mt-12 grid gap-6 lg:grid-cols-3">
          {PRICING_TIERS.map((tier) => (
            <div
              key={tier.name}
              className={`flex flex-col rounded-2xl border p-6 ${
                tier.highlight
                  ? "border-sky-500 bg-white shadow-lg ring-2 ring-sky-500/20 dark:bg-slate-900"
                  : "border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900"
              }`}
            >
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{tier.name}</h3>
              <p className="mt-2">
                <span className="text-3xl font-bold text-slate-900 dark:text-white">{tier.price}</span>
                <span className="text-sm text-slate-500">{tier.period}</span>
              </p>
              <ul className="mt-6 flex-1 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                {tier.bullets.map((b) => (
                  <li key={b}>• {b}</li>
                ))}
              </ul>
              <Link
                href={tier.name === "Enterprise" ? "/contact" : `${APP_URL}/register`}
                className={`mt-6 block rounded-lg py-3 text-center text-sm font-semibold ${
                  tier.highlight ? "bg-slate-900 text-white hover:bg-slate-800" : "border border-slate-200 hover:bg-slate-50 dark:border-slate-600 dark:hover:bg-slate-800"
                }`}
              >
                {tier.cta}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
