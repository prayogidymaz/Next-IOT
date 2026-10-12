import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Documentation",
};

export default function DocsPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-16 md:px-6">
      <h1 className="text-4xl font-semibold">Documentation</h1>
      <p className="mt-4 text-slate-600">
        Dokumentasi teknis lengkap sedang dipublikasikan. Sementara, mulai dari{" "}
        <Link href="/features" className="text-sky-600 hover:underline">features overview</Link> atau hubungi tim untuk
        onboarding.
      </p>
    </div>
  );
}
