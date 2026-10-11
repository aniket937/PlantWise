import Link from "next/link";
import { Filter, Search, Sprout } from "lucide-react";

import { EmptyState, Notice } from "@/components/feedback";
import { PlantCard } from "@/components/plant-card";
import { getPlants } from "@/lib/api";
import { DIFFICULTY_OPTIONS, LIFECYCLE_OPTIONS } from "@/lib/format";

export const metadata = {
  title: "Explore plants",
  description:
    "Browse the PlantWise plant library by name, lifecycle and growing difficulty.",
};

interface ExplorePageProps {
  searchParams: Promise<{
    query?: string;
    lifecycle?: string;
    difficulty?: string;
  }>;
}

const PAGE_SIZE = 24;

export default async function ExplorePage({ searchParams }: ExplorePageProps) {
  const params = await searchParams;
  const query = (params.query ?? "").trim();
  const lifecycle = params.lifecycle ?? "";
  const difficulty = params.difficulty ?? "";

  const result = await getPlants({
    query: query || undefined,
    lifecycle: lifecycle || undefined,
    difficulty: difficulty || undefined,
    limit: PAGE_SIZE,
  });

  const hasFilters = Boolean(query || lifecycle || difficulty);

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <header className="max-w-2xl">
        <p className="text-xs font-semibold uppercase tracking-wide text-accent">
          Plant library
        </p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-foreground">
          Explore plants
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          Every profile records what the crop needs to grow. Open a profile to see those
          requirements in full, then check them against a place you care about.
        </p>
      </header>

      <form
        method="get"
        className="mt-8 rounded-xl border border-border bg-surface p-4 shadow-[var(--shadow)]"
      >
        <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
          <div className="space-y-2">
            <label htmlFor="query" className="block text-sm font-medium text-foreground">
              Search by name, family or keyword
            </label>
            <div className="relative">
              <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted">
                <Search className="size-4" aria-hidden="true" />
              </span>
              <input
                id="query"
                name="query"
                type="search"
                defaultValue={query}
                placeholder="e.g. tomato, brassica, drought tolerant"
                className="w-full rounded-lg border border-border bg-surface py-2.5 pl-9 pr-3 text-sm text-foreground placeholder:text-muted"
              />
            </div>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary-hover sm:w-auto"
            >
              <Filter className="size-4" aria-hidden="true" />
              Apply filters
            </button>
          </div>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div className="space-y-2">
            <label htmlFor="lifecycle" className="block text-sm font-medium text-foreground">
              Lifecycle
            </label>
            <select
              id="lifecycle"
              name="lifecycle"
              defaultValue={lifecycle}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-foreground"
            >
              <option value="">Any lifecycle</option>
              {LIFECYCLE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label htmlFor="difficulty" className="block text-sm font-medium text-foreground">
              Difficulty
            </label>
            <select
              id="difficulty"
              name="difficulty"
              defaultValue={difficulty}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-foreground"
            >
              <option value="">Any difficulty</option>
              {DIFFICULTY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {hasFilters ? (
          <p className="mt-4 text-xs text-muted">
            <Link href="/explore" className="text-primary underline underline-offset-2">
              Clear all filters
            </Link>
          </p>
        ) : null}
      </form>

      {!result.ok ? (
        <div className="mt-8">
          <Notice tone="warning" title="The plant library could not be loaded">
            {result.message}
          </Notice>
        </div>
      ) : null}

      {result.ok ? (
        <section className="mt-8" aria-live="polite">
          <p className="text-sm text-muted">
            {result.data.total === 0
              ? "No plants matched."
              : `${result.data.total} ${result.data.total === 1 ? "plant" : "plants"} found${
                  query ? ` for “${query}”` : ""
                }.`}
          </p>

          {result.data.items.length > 0 ? (
            <ul className="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {result.data.items.map((plant, index) => (
                <li key={plant.slug}>
                  <PlantCard plant={plant} preload={index === 0} />
                </li>
              ))}
            </ul>
          ) : (
            <div className="mt-5 space-y-4">
              <EmptyState
                icon={<Sprout className="size-5" aria-hidden="true" />}
                title="Nothing matched that search"
                description="Try a shorter or more general term, or clear the filters to see the whole library."
                action={
                  <Link
                    href="/explore"
                    className="inline-flex items-center rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-surface-2"
                  >
                    Show every plant
                  </Link>
                }
              />

              {result.data.suggestions.length > 0 ? (
                <div className="rounded-lg border border-border bg-surface p-4">
                  <p className="text-sm font-medium text-foreground">Did you mean</p>
                  <ul className="mt-2 flex flex-wrap gap-2">
                    {result.data.suggestions.map((suggestion) => {
                      const match = /^(.*) \((.*)\)$/.exec(suggestion);
                      const label = match ? match[1] : suggestion;
                      const slug = match ? match[2] : suggestion;
                      return (
                        <li key={slug}>
                          <Link
                            href={`/plants/${slug}`}
                            className="rounded-full border border-border px-3 py-1.5 text-sm text-foreground hover:bg-surface-2"
                          >
                            {label}
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ) : null}
            </div>
          )}
        </section>
      ) : null}
    </div>
  );
}
