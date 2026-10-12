import { Logo } from "@next-iot/ui";
import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-12 md:grid-cols-4 md:px-6">
        <div>
          <Logo />
          <p className="mt-3 text-sm text-slate-500">Platform IoT komersial Indonesia — dari edge sampai billing.</p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Product</p>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            <li><Link href="/features">Features</Link></li>
            <li><Link href="/pricing">Pricing</Link></li>
            <li><Link href="/docs">Docs</Link></li>
          </ul>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Company</p>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            <li><Link href="/about">About</Link></li>
            <li><Link href="/contact">Contact</Link></li>
          </ul>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Legal</p>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            <li><Link href="/contact">Privacy</Link></li>
            <li><Link href="/contact">Terms</Link></li>
          </ul>
        </div>
      </div>
      <p className="border-t border-slate-200 py-6 text-center text-xs text-slate-400">
        © {new Date().getFullYear()} Next-IoT. All rights reserved.
      </p>
    </footer>
  );
}
