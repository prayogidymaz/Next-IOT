import { Card } from "@next-iot/ui";

import { HOME_FEATURES } from "@/lib/landing-content";

export function FeaturesHomeSection() {
  return (
    <section className="border-y border-slate-100 bg-slate-50 py-20 dark:border-slate-800 dark:bg-slate-900/30">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-center text-3xl font-semibold text-slate-900 dark:text-white">Fitur platform</h2>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {HOME_FEATURES.map((f) => (
            <Card key={f.title} className="p-6 dark:border-slate-700 dark:bg-slate-900" shadow="sm">
              <span className="text-2xl">{f.emoji}</span>
              <h3 className="mt-3 font-semibold text-slate-900 dark:text-white">{f.title}</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{f.body}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
