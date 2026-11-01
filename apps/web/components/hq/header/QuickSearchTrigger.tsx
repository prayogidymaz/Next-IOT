"use client";

import { Search } from "lucide-react";

type Props = {
  onOpen: () => void;
};

export function QuickSearchTrigger({ onOpen }: Props) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card text-foreground hover:bg-muted"
      aria-label="Quick search"
      title="Quick search (⌘K)"
    >
      <Search className="h-4 w-4" />
    </button>
  );
}
