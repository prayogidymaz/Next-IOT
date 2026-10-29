import Link from "next/link";

export default function AnalyticsYieldRoute() {
  return (
    <div className="space-y-3 p-6">
      <h1 className="text-2xl font-semibold text-stone-900">Yield forecast</h1>
      <p className="text-sm text-stone-600">Per-farm yield analytics live under Smart Agriculture.</p>
      <Link href="/agriculture" className="text-sm font-medium text-emerald-800 hover:underline">
        Open Smart Agriculture →
      </Link>
    </div>
  );
}
