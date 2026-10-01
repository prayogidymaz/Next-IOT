"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Cpu,
  Menu,
  Shield,
  X,
  Zap,
} from "lucide-react";
import { useState } from "react";

import { DashboardShowcase } from "./DashboardShowcase";
import { MarketingFeaturesBento } from "./MarketingFeaturesBento";

const NAV_LINKS = [
  { href: "#platform", label: "Platform" },
  { href: "#solutions", label: "Solutions" },
  { href: "#automation", label: "Automation" },
  { href: "#pricing", label: "Pricing" },
];

const METRICS = [
  { label: "Platform uptime", value: "99.97%", sub: "SLA-backed edge + cloud" },
  { label: "Devices managed", value: "2.4M+", sub: "Multi-tenant fleets" },
  { label: "Telemetry ingest", value: "<120ms", sub: "P95 ingest latency" },
  { label: "Regions", value: "12", sub: "Global deployment zones" },
];

export function PublicLandingPage() {
  const reduceMotion = useReducedMotion();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-cream-page text-ink-primary">
      <header className="sticky top-0 z-50 border-b border-cream-border bg-cream-alt/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 md:px-8">
          <Link href="/" className="flex items-center gap-2 font-bold tracking-tight">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent-emerald-soft text-sm font-bold text-accent-emerald">
              N
            </span>
            <span>
              Next-IoT
              <span className="ml-1 text-xs font-normal text-ink-secondary">Enterprise</span>
            </span>
          </Link>

          <nav className="hidden items-center gap-8 md:flex">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm text-ink-secondary transition-colors hover:text-ink-primary"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div className="hidden items-center gap-3 md:flex">
            <Link
              href="/login"
              className="text-sm font-medium text-ink-secondary transition-colors hover:text-ink-primary"
            >
              Sign In
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-2xl bg-ink-primary px-4 py-2.5 text-sm font-semibold text-white shadow-card transition-all duration-300 ease-out hover:scale-[1.02] active:scale-95"
            >
              Launch App
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <button
            type="button"
            className="rounded-lg p-2 text-ink-secondary md:hidden"
            aria-label="Toggle menu"
            onClick={() => setMobileOpen((o) => !o)}
          >
            {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {mobileOpen && (
          <div className="border-t border-cream-border px-4 py-4 md:hidden">
            <nav className="flex flex-col gap-3">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  className="text-sm text-ink-secondary"
                  onClick={() => setMobileOpen(false)}
                >
                  {link.label}
                </a>
              ))}
              <Link href="/login" className="mt-2 text-sm font-medium text-accent-emerald">
                Launch App →
              </Link>
            </nav>
          </div>
        )}
      </header>

      <main>
        <section id="platform" className="relative overflow-hidden px-4 pb-16 pt-16 md:px-8 md:pt-24">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(16,185,129,0.12),transparent)]" />
          <div className="relative mx-auto grid max-w-6xl gap-12 lg:grid-cols-2 lg:items-center">
            <motion.div
              initial={reduceMotion ? false : { opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ type: "spring", stiffness: 280, damping: 28 }}
            >
              <p className="inline-flex items-center gap-2 rounded-full border border-cream-border bg-white px-3 py-1 text-xs font-medium text-ink-secondary shadow-sm">
                <Cpu className="h-3.5 w-3.5 text-accent-emerald" />
                Edge + Cloud unified platform
              </p>
              <h1 className="mt-6 text-4xl font-bold leading-tight tracking-tight md:text-5xl lg:text-[3.25rem]">
                The Next-Gen Enterprise IoT & Edge Automation Platform
              </h1>
              <p className="mt-6 max-w-xl text-lg leading-relaxed text-ink-secondary">
                Connect devices, orchestrate automations, and operate multi-tenant fleets with glass-smooth operator
                UX — inspired by Smart Life, engineered for enterprise scale.
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
                <Link
                  href="/register"
                  className="inline-flex items-center gap-2 rounded-2xl bg-accent-emerald px-6 py-3.5 text-sm font-semibold text-white shadow-card transition-all duration-300 ease-out hover:scale-[1.02] active:scale-95"
                >
                  Start Free Trial
                  <Zap className="h-4 w-4" />
                </Link>
                <a
                  href="#automation"
                  className="inline-flex items-center gap-2 rounded-2xl border border-cream-border bg-white px-6 py-3.5 text-sm font-semibold text-ink-primary shadow-sm transition-all duration-300 ease-out hover:scale-[1.02] active:scale-95"
                >
                  View Live Demo
                  <BarChart3 className="h-4 w-4" />
                </a>
              </div>
            </motion.div>

            <motion.div
              initial={reduceMotion ? false : { opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1, type: "spring", stiffness: 260, damping: 26 }}
              className="cream-card p-6 shadow-card-md"
            >
              <div className="grid grid-cols-2 gap-4">
                {[
                  { icon: Shield, label: "SOC2-ready audit" },
                  { icon: Zap, label: "Sub-second telemetry" },
                  { icon: Cpu, label: "Edge automation" },
                  { icon: BarChart3, label: "Analytics export" },
                ].map(({ icon: Icon, label }) => (
                  <div
                    key={label}
                    className="rounded-2xl border border-cream-border bg-cream-alt p-4 transition-transform duration-300 hover:scale-[1.02]"
                  >
                    <Icon className="mb-2 h-5 w-5 text-accent-cobalt" />
                    <p className="text-sm font-medium text-ink-primary">{label}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        <DashboardShowcase />
        <MarketingFeaturesBento />

        <section className="border-y border-cream-border bg-white py-16">
          <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 px-4 md:grid-cols-4 md:px-8">
            {METRICS.map((m) => (
              <div key={m.label}>
                <p className="text-3xl font-bold tabular-nums text-ink-primary md:text-4xl">{m.value}</p>
                <p className="mt-1 text-sm font-medium text-ink-secondary">{m.label}</p>
                <p className="mt-1 text-xs text-ink-tertiary">{m.sub}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="pricing" className="mx-auto max-w-6xl px-4 py-20 text-center md:px-8">
          <h2 className="text-3xl font-bold text-ink-primary">Ready to deploy at enterprise scale?</h2>
          <p className="mx-auto mt-3 max-w-xl text-ink-secondary">
            Start with the live dashboard demo, then connect your API tenant and Flutter operator clients.
          </p>
          <Link
            href="/dashboard"
            className="mt-8 inline-flex items-center gap-2 rounded-2xl bg-ink-primary px-8 py-3.5 text-sm font-semibold text-white shadow-card transition-all duration-300 hover:scale-[1.02] active:scale-95"
          >
            Launch Control Center
            <ArrowRight className="h-4 w-4" />
          </Link>
        </section>
      </main>

      <footer className="border-t border-cream-border bg-cream-muted px-4 py-12 md:px-8">
        <div className="mx-auto flex max-w-6xl flex-col gap-8 md:flex-row md:justify-between">
          <div>
            <p className="text-lg font-bold">Next-IoT</p>
            <p className="mt-2 max-w-xs text-sm text-ink-secondary">
              Enterprise IoT, edge automation, and operator experiences — built for regulated, multi-tenant fleets.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-8 text-sm sm:grid-cols-3">
            <div>
              <p className="font-semibold text-ink-primary">Product</p>
              <ul className="mt-3 space-y-2 text-ink-secondary">
                <li>
                  <a href="#platform">Platform</a>
                </li>
                <li>
                  <a href="#solutions">Solutions</a>
                </li>
                <li>
                  <Link href="/dashboard">Dashboard</Link>
                </li>
                <li>
                  <Link href="/cyberdeck">Cyberdeck PTT</Link>
                </li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-ink-primary">Company</p>
              <ul className="mt-3 space-y-2 text-ink-secondary">
                <li>Security</li>
                <li>Compliance</li>
                <li>Contact</li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-ink-primary">Legal</p>
              <ul className="mt-3 space-y-2 text-ink-secondary">
                <li>Privacy</li>
                <li>Terms</li>
                <li>SLA</li>
              </ul>
            </div>
          </div>
        </div>
        <p className="mx-auto mt-10 max-w-6xl text-center text-xs text-ink-tertiary">
          © {new Date().getFullYear()} Next-IoT. All rights reserved.
        </p>
      </footer>
    </div>
  );
}
