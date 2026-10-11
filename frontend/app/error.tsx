"use client";

import Link from "next/link";
import { Compass, RotateCcw, TriangleAlert } from "lucide-react";

export default function GlobalError({
  error,
  retry,
}: {
  error: Error & { digest?: string };
  retry: () => void;
}) {
  return (
    <div className="mx-auto flex max-w-2xl flex-col items-start px-4 py-20 sm:px-6">
      <span className="flex size-11 items-center justify-center rounded-full bg-fail-soft text-fail">
        <TriangleAlert className="size-5" aria-hidden="true" />
      </span>
      <h1 className="mt-4 text-2xl font-semibold tracking-tight text-foreground">
        Something went wrong on this page
      </h1>
      <p className="mt-3 text-sm leading-relaxed text-muted">
        The page could not be rendered. Nothing was saved or submitted, so it is safe to try
        again.
      </p>
      {error.digest ? (
        <p className="mt-2 text-xs text-muted">
          Reference for the logs: <code className="text-foreground">{error.digest}</code>
        </p>
      ) : null}

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={retry}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary-hover"
        >
          <RotateCcw className="size-4" aria-hidden="true" />
          Try again
        </button>
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-lg border border-border px-4 py-2.5 text-sm font-medium text-foreground hover:bg-surface-2"
        >
          <Compass className="size-4" aria-hidden="true" />
          Back to the home page
        </Link>
      </div>
    </div>
  );
}
