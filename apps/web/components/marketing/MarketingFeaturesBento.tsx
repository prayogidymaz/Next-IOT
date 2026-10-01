"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  Activity,
  GitBranch,
  Layers,
  Radio,
  ShieldCheck,
} from "lucide-react";

const FEATURES = [
  {
    title: "Visual Automation Studio",
    description: "Drag-and-drop pipeline builder with dry-run validation and JSON import/export.",
    icon: GitBranch,
    accent: "from-violet-500/20 to-indigo-500/5",
    iconColor: "text-violet-300",
    span: "md:col-span-2",
  },
  {
    title: "OTA Rollouts",
    description: "Fleet firmware releases, staged rollouts, and device-side update checks.",
    icon: Radio,
    accent: "from-sky-500/20 to-blue-500/5",
    iconColor: "text-sky-300",
    span: "",
  },
  {
    title: "Multi-Tenant RBAC",
    description: "Organization switching, role tiers, and permission guards across the stack.",
    icon: ShieldCheck,
    accent: "from-emerald-500/20 to-teal-500/5",
    iconColor: "text-emerald-300",
    span: "",
  },
  {
    title: "Time-Series Analytics",
    description: "Bucketed telemetry analytics, multi-metric charts, and CSV export center.",
    icon: Activity,
    accent: "from-amber-500/20 to-orange-500/5",
    iconColor: "text-amber-300",
    span: "md:col-span-2",
  },
  {
    title: "Enterprise Audit Logs",
    description: "Immutable audit trail with filters, CSV export, and compliance-ready events.",
    icon: Layers,
    accent: "from-rose-500/20 to-pink-500/5",
    iconColor: "text-rose-300",
    span: "md:col-span-3 lg:col-span-1",
  },
];

export function MarketingFeaturesBento() {
  const reduceMotion = useReducedMotion();

  return (
    <section id="solutions" className="mx-auto max-w-6xl px-4 py-20 md:px-8">
      <div className="mb-10 max-w-2xl">
        <p className="text-sm font-semibold uppercase tracking-widest text-tuya-green">Platform modules</p>
        <h2 className="mt-2 text-3xl font-bold tracking-tight text-white md:text-4xl">
          Enterprise IoT building blocks, unified
        </h2>
        <p className="mt-3 text-slate-400">
          From edge ingestion to operator dashboards — five core modules power the Next-IoT control plane.
        </p>
      </div>

      <motion.div
        initial={reduceMotion ? false : "hidden"}
        whileInView="show"
        viewport={{ once: true, margin: "-80px" }}
        variants={{
          hidden: { opacity: 0 },
          show: { opacity: 1, transition: { staggerChildren: 0.07 } },
        }}
        className="grid grid-cols-1 gap-4 md:grid-cols-3 md:gap-5"
      >
        {FEATURES.map((feature) => {
          const Icon = feature.icon;
          return (
            <motion.article
              key={feature.title}
              variants={{
                hidden: { opacity: 0, y: 20 },
                show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } },
              }}
              whileHover={reduceMotion ? undefined : { scale: 1.02 }}
              className={`group rounded-[28px] border border-white/10 bg-slate-900/60 p-6 backdrop-blur-xl transition-all duration-300 ease-out ${feature.span}`}
            >
              <div
                className={`mb-5 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br ${feature.accent} ring-1 ring-white/10`}
              >
                <Icon className={`h-6 w-6 ${feature.iconColor}`} strokeWidth={1.75} />
              </div>
              <h3 className="text-lg font-bold text-white">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">{feature.description}</p>
            </motion.article>
          );
        })}
      </motion.div>
    </section>
  );
}
