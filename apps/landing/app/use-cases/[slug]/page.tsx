import { Card } from "@next-iot/ui";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { USE_CASES, type UseCaseSlug } from "@/lib/site";

type PageProps = { params: Promise<{ slug: string }> };

export function generateStaticParams(): { slug: UseCaseSlug }[] {
  return Object.keys(USE_CASES).map((slug) => ({ slug: slug as UseCaseSlug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const uc = USE_CASES[slug as UseCaseSlug];
  if (!uc) return { title: "Use case" };
  return { title: uc.title, description: uc.description };
}

export default async function UseCasePage({ params }: PageProps) {
  const { slug } = await params;
  const uc = USE_CASES[slug as UseCaseSlug];
  if (!uc) notFound();

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 md:px-6">
      <Link href="/" className="text-sm text-sky-600 hover:underline">← Home</Link>
      <p className="mt-6 text-4xl">{uc.emoji}</p>
      <h1 className="mt-2 text-4xl font-semibold">{uc.title}</h1>
      <p className="mt-4 text-lg text-slate-600">{uc.description}</p>
      <Card className="mt-8 p-6" shadow="sm">
        <ul className="space-y-2 text-slate-700">
          {uc.bullets.map((b) => (
            <li key={b}>• {b}</li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
