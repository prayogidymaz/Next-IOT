"use client";

import React, { type ErrorInfo, type ReactNode } from "react";

type Props = {
  children: ReactNode;
  fallbackTitle?: string;
};

type State = {
  error: Error | null;
};

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("[ErrorBoundary]", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="text-lg font-semibold text-foreground">{this.props.fallbackTitle ?? "Something went wrong"}</h2>
          <p className="mt-2 text-sm text-muted-foreground">{this.state.error.message}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded-lg bg-foreground px-3 py-2 text-sm text-background"
              onClick={() => this.setState({ error: null })}
            >
              Try again
            </button>
            <a
              className="rounded-lg border border-border px-3 py-2 text-sm text-foreground"
              href="https://github.com/next-iot/next-iot/issues/new"
              target="_blank"
              rel="noreferrer"
            >
              Report issue
            </a>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
