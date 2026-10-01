"use client";

import { Globe, ImagePlus, Palette } from "lucide-react";
import { useState } from "react";

import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";

export default function TenantBrandingPage() {
  const [primary, setPrimary] = useState("#1A1A1A");
  const [accent, setAccent] = useState("#10B981");
  const [domain, setDomain] = useState("ops.acme-iot.com");

  return (
    <HqPageContent description="Upload brand assets, custom domains, and cream-theme tokens for white-label tenants.">
      <div className="grid gap-6 lg:grid-cols-2">
        <CreamCard className="p-5">
          <h2 className="flex items-center gap-2 font-semibold text-ink-primary">
            <ImagePlus className="h-5 w-5 text-accent-violet" />
            Brand kit
          </h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {["Logo (SVG/PNG)", "Favicon", "Splash / OG"].map((label) => (
              <button
                key={label}
                type="button"
                className="flex h-28 flex-col items-center justify-center rounded-xl border border-dashed border-cream-border bg-cream-alt text-sm text-ink-secondary transition hover:border-ink-tertiary hover:bg-white"
              >
                <ImagePlus className="mb-2 h-5 w-5" />
                Upload {label}
              </button>
            ))}
          </div>
        </CreamCard>

        <CreamCard className="p-5">
          <h2 className="flex items-center gap-2 font-semibold text-ink-primary">
            <Globe className="h-5 w-5 text-accent-cobalt" />
            Custom domain
          </h2>
          <label className="mt-4 block text-sm text-ink-secondary">
            Hostname
            <input
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="mt-1.5 w-full rounded-xl border border-cream-border bg-white px-4 py-3 text-ink-primary outline-none ring-accent-cobalt/30 focus:ring-2"
            />
          </label>
          <p className="mt-2 text-xs text-ink-tertiary">TLS provisioning hooks to Cloudflare / Tailscale tunnel.</p>
        </CreamCard>

        <CreamCard className="p-5 lg:col-span-2">
          <h2 className="flex items-center gap-2 font-semibold text-ink-primary">
            <Palette className="h-5 w-5 text-accent-amber" />
            Color theme picker
          </h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <label className="text-sm text-ink-secondary">
              Primary ink
              <div className="mt-2 flex items-center gap-3">
                <input
                  type="color"
                  value={primary}
                  onChange={(e) => setPrimary(e.target.value)}
                  className="h-10 w-14 cursor-pointer rounded-lg border border-cream-border bg-white"
                />
                <span className="font-mono text-xs">{primary}</span>
              </div>
            </label>
            <label className="text-sm text-ink-secondary">
              Accent (pastel base)
              <div className="mt-2 flex items-center gap-3">
                <input
                  type="color"
                  value={accent}
                  onChange={(e) => setAccent(e.target.value)}
                  className="h-10 w-14 cursor-pointer rounded-lg border border-cream-border bg-white"
                />
                <span className="font-mono text-xs">{accent}</span>
              </div>
            </label>
          </div>
          <div
            className="mt-6 rounded-2xl border border-cream-border p-6 shadow-card"
            style={{ background: "#FBFBF9", color: primary }}
          >
            <p className="text-sm opacity-70">Live preview — Warm Cream shell</p>
            <p className="mt-2 text-lg font-semibold">Acme IoT Operator HQ</p>
            <button
              type="button"
              className="mt-4 rounded-xl px-4 py-2 text-sm font-medium text-white"
              style={{ backgroundColor: accent }}
            >
              Launch branded app
            </button>
          </div>
          <button type="button" className="hq-btn-primary mt-5">
            Save white-label profile
          </button>
        </CreamCard>
      </div>
    </HqPageContent>
  );
}
