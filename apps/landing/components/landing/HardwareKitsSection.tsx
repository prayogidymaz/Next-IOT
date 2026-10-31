import Link from "next/link";

import { HARDWARE_KITS } from "@/lib/landing-content";

export function HardwareKitsSection() {
  return (
    <section className="py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <h2 className="text-3xl font-semibold text-slate-900 dark:text-white">Hardware kit</h2>
          <Link href="/features" className="text-sm font-medium text-sky-600 hover:underline">
            Lihat katalog lengkap →
          </Link>
        </div>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {HARDWARE_KITS.map((kit) => (
            <div
              key={kit.name}
              className="rounded-xl border border-slate-200 p-5 dark:border-slate-700 dark:bg-slate-900/50"
            >
              <span className="text-2xl">{kit.emoji}</span>
              <h3 className="mt-2 font-semibold text-slate-900 dark:text-white">{kit.name}</h3>
              <p className="text-sm text-slate-500">{kit.price}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
