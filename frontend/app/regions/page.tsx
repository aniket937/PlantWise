import Link from "next/link";
import { ArrowRight, Globe, MapPin } from "lucide-react";

import { EmptyState, Notice } from "@/components/feedback";
import { getPlantsWithRegions } from "@/lib/api";

export const metadata = {
  title: "Documented growing regions",
  description:
    "Places where crops in the PlantWise library are recorded as being cultivated, kept separate from any suitability judgement.",
};

export default async function RegionsIndexPage() {
  const result = await getPlantsWithRegions();

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <header className="max-w-2xl">
        <p className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-accent">
          <Globe className="size-3.5" aria-hidden="true" />
          Evidence map
        </p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-foreground">
          Documented growing regions
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          A region listed here means the crop is recorded as cultivated there. It is
          evidence about the crop&apos;s real-world range, and it is deliberately kept apart
          from any judgement about whether the crop would suit your own site.
        </p>
      </header>

      {!result.ok ? (
        <div className="mt-8">
          <Notice tone="warning" title="Regions could not be loaded">
            {result.message}
          </Notice>
        </div>
      ) : result.data.items.length === 0 ? (
        <div className="mt-8">
          <EmptyState
            icon={<MapPin className="size-5" aria-hidden="true" />}
            title="No regions recorded yet"
            description="Once cultivation regions are recorded against plants, they will be listed here."
          />
        </div>
      ) : (
        <ul className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {result.data.items.map((item) => (
            <li key={item.slug}>
              <Link
                href={`/regions/${item.slug}`}
                className="group flex h-full flex-col rounded-xl border border-border bg-surface p-5 shadow-[var(--shadow)] transition-colors hover:border-border-strong"
              >
                <h2 className="text-base font-semibold tracking-tight text-foreground">
                  {item.common_name}
                </h2>
                <p className="text-sm italic text-muted">{item.scientific_name}</p>
                <p className="mt-3 flex-1 text-sm text-muted">
                  {item.region_count}{" "}
                  {item.region_count === 1 ? "documented region" : "documented regions"}
                </p>
                <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-primary">
                  View the map
                  <ArrowRight
                    className="size-4 transition-transform group-hover:translate-x-0.5"
                    aria-hidden="true"
                  />
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
