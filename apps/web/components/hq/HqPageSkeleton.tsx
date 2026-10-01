type HqPageSkeletonProps = {
  variant?: "overview" | "studio" | "control" | "settings";
};

export function HqPageSkeleton({ variant = "overview" }: HqPageSkeletonProps) {
  return (
    <div className="animate-pulse space-y-6 p-6 md:p-8">
      <div className="space-y-2">
        <div className="h-8 w-48 rounded-lg bg-cream-muted" />
        <div className="h-4 w-96 max-w-full rounded bg-cream-muted" />
      </div>

      {variant === "control" ? (
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="h-32 rounded-2xl bg-cream-muted lg:col-span-3" />
          <div className="h-64 rounded-2xl bg-cream-muted lg:col-span-2" />
          <div className="h-64 rounded-2xl bg-cream-muted" />
        </div>
      ) : null}

      {variant === "studio" ? (
        <div className="grid gap-4 lg:grid-cols-[220px_1fr]">
          <div className="h-[420px] rounded-2xl bg-cream-muted" />
          <div className="h-[420px] rounded-2xl bg-cream-muted" />
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-28 rounded-2xl bg-cream-muted" />
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="h-72 rounded-2xl bg-cream-muted lg:col-span-2" />
        <div className="h-72 rounded-2xl bg-cream-muted lg:col-span-3" />
      </div>

      {variant === "settings" ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-14 rounded-xl bg-cream-muted" />
          ))}
        </div>
      ) : null}
    </div>
  );
}
