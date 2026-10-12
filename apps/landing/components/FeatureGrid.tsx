"use client";

import { Card } from "@next-iot/ui";
import { motion } from "framer-motion";

import { FEATURES } from "@/lib/site";

export function FeatureGrid() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-20 md:px-6">
      <h2 className="text-center text-3xl font-semibold text-slate-900">Semua yang Anda butuhkan untuk scale IoT</h2>
      <p className="mx-auto mt-3 max-w-2xl text-center text-slate-600">
        Built for operators who need reliability, security, and speed to market.
      </p>
      <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.05 }}
          >
            <Card className="h-full p-6" hover shadow="sm">
              <span className="text-2xl" aria-hidden>{f.emoji}</span>
              <h3 className="mt-4 text-lg font-semibold text-slate-900">{f.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{f.body}</p>
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
