import { Card } from "@next-iot/ui";

import { TESTIMONIALS } from "@/lib/landing-content";

export function TestimonialsHomeSection() {
  return (
    <section className="border-t border-slate-100 bg-slate-50 py-20 dark:border-slate-800 dark:bg-slate-900/30">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-center text-2xl font-semibold text-slate-900 dark:text-white">Testimonial</h2>
        <p className="mt-2 text-center text-xs text-amber-700 dark:text-amber-400">
          Testimonial pilot customer akan di-update setelah program design partner.
        </p>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {TESTIMONIALS.map((t) => (
            <Card key={t.name} className="p-6 dark:border-slate-700 dark:bg-slate-900" shadow="sm">
              <p className="text-sm text-slate-700 dark:text-slate-300">&ldquo;{t.quote}&rdquo;</p>
              <p className="mt-4 text-sm font-semibold text-slate-900 dark:text-white">{t.name}</p>
              <p className="text-xs text-slate-500">{t.role}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
