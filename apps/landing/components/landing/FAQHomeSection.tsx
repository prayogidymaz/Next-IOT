import { FAQ_ITEMS } from "@/lib/landing-content";

export function FAQHomeSection() {
  return (
    <section id="faq" className="py-20">
      <div className="mx-auto max-w-3xl px-4 md:px-6">
        <h2 className="text-center text-3xl font-semibold text-slate-900 dark:text-white">FAQ</h2>
        <dl className="mt-10 space-y-6">
          {FAQ_ITEMS.map((item) => (
            <div key={item.q} className="rounded-xl border border-slate-200 p-5 dark:border-slate-700">
              <dt className="font-semibold text-slate-900 dark:text-white">{item.q}</dt>
              <dd className="mt-2 text-sm text-slate-600 dark:text-slate-300">{item.a}</dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
