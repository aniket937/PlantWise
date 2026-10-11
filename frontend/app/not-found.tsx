import Link from "next/link";
import { Compass, Search, Sprout } from "lucide-react";

export default function NotFound() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col items-start px-4 py-20 sm:px-6">
      <span className="flex size-11 items-center justify-center rounded-full bg-sage text-primary">
        <Sprout className="size-5" aria-hidden="true" />
      </span>
      <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-accent">
        404
      </p>
      <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
        This page does not exist
      </h1>
      <p className="mt-3 text-sm leading-relaxed text-muted">
        The link may be out of date, or the plant profile may have been renamed. The library
        and the location check are both one click away.
      </p>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link
          href="/explore"
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary-hover"
        >
          <Search className="size-4" aria-hidden="true" />
          Explore the plant library
        </Link>
        <Link
          href="/location"
          className="inline-flex items-center gap-2 rounded-lg border border-border px-4 py-2.5 text-sm font-medium text-foreground hover:bg-surface-2"
        >
          <Compass className="size-4" aria-hidden="true" />
          Check a location
        </Link>
      </div>
    </div>
  );
}
