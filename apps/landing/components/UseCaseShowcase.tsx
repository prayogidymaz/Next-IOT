import { Card } from "@next-iot/ui";
import Link from "next/link";

import { USE_CASES, type UseCaseSlug } from "@/lib/site";

const SLUGS: UseCaseSlug[] = ["farming", "drone-sar", "smart-building", "industrial"];

export function UseCaseShowcase() {
  return (
    <section className="bg-slate-50 py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-3xl font-semibold text-slate-900">Use cases by vertical</h2>
        <div className="mt-10 grid gap-6 md:grid-cols-2">
          {SLUGS.map((slug) => {
            const uc = USE_CASES[slug];
            return (
              <Card key={slug} className="p-6" hover>
                <span className="text-3xl">{uc.emoji}</span>
                <h3 className="mt-3 text-xl font-semibold">{uc.title}</h3>
                <ul className="mt-3 space-y-1 text-sm text-slate-600">
                  {uc.bullets.map((b) => (
                    <li key={b}>• {b}</li>
                  ))}
                </ul>
                <Link href={`/use-cases/${slug}`} className="mt-4 inline-block text-sm font-medium text-sky-600 hover:underline">
                  Learn more →
                </Link>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}
