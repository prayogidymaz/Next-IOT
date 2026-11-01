"use client";

import { Button } from "@/components/ui/button";

type Props = {
  error: string;
  onRetry?: () => void;
};

export function ErrorState({ error, onRetry }: Props) {
  return (
    <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-6 text-center">
      <p className="text-sm font-medium text-foreground">Something went wrong</p>
      <p className="mt-1 text-sm text-muted-foreground">{error}</p>
      {onRetry ? (
        <Button type="button" variant="outline" className="mt-4" onClick={onRetry}>
          Retry
        </Button>
      ) : null}
    </div>
  );
}
