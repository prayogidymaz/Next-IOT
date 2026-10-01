import { Suspense, type ReactNode } from "react";

type StudioRouteShellProps = {
  meta: ReactNode;
  children: ReactNode;
};

export function StudioRouteShell({ meta, children }: StudioRouteShellProps) {
  return (
    <div className="space-y-4">
      <Suspense
        fallback={<div className="h-6 w-64 animate-pulse rounded-full bg-cream-muted" aria-hidden />}
      >
        {meta}
      </Suspense>
      {children}
    </div>
  );
}
