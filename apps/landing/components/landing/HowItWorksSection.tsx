import { HOW_IT_WORKS } from "@/lib/landing-content";

export function HowItWorksSection() {
  return (
    <section className="py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-center text-3xl font-semibold text-slate-900 dark:text-white">Cara kerja</h2>
        <ol className="mt-12 grid gap-8 md:grid-cols-3">
          {HOW_IT_WORKS.map((item) => (
            <li key={item.step} className="relative rounded-2xl border border-slate-200 p-6 dark:border-slate-700">
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-sky-600 text-sm font-bold text-white">
                {item.step}
              </span>
              <h3 className="mt-4 text-lg font-semibold text-slate-900 dark:text-white">{item.title}</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{item.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
