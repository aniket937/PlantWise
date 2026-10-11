import Link from "next/link";
import { Compass, Info, MapPin, Thermometer } from "lucide-react";

import { AnalysisForm } from "@/components/analysis-form";
import { Notice } from "@/components/feedback";
import { getPlants } from "@/lib/api";

export const metadata = {
  title: "Check a location",
  description:
    "Pick a plant and a place to compare the crop's documented requirements against long-term local climate records.",
};

interface LocationPageProps {
  searchParams: Promise<{ plant?: string }>;
}

const FACTS = [
  {
    icon: MapPin,
    title: "Pick a place, not a region label",
    detail:
      "Coordinates are what the climate record is keyed on. Searching a town name resolves it to a single point you can see before you continue.",
  },
  {
    icon: Thermometer,
    title: "Ten years of daily records",
    detail:
      "The baseline is a decade of daily minimum and maximum temperatures, precipitation and frost counts — not a single recent season.",
  },
  {
    icon: Info,
    title: "Gaps are stated, not filled",
    detail:
      "Anything you leave blank, and anything the record cannot answer, is reported as not assessed rather than assumed.",
  },
] as const;

export default async function LocationPage({ searchParams }: LocationPageProps) {
  const params = await searchParams;
  const plants = await getPlants({ limit: 100 });

  if (!plants.ok || plants.data.items.length === 0) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Check a location
        </h1>
        <div className="mt-6">
          <Notice tone="warning" title="The plant library is unavailable">
            {plants.ok
              ? "The library is empty. Seed the database by starting the backend once, then reload."
              : plants.message}
          </Notice>
        </div>
        <Link
          href="/"
          className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
        >
          Back to the home page
        </Link>
      </div>
    );
  }

  const options = plants.data.items.map((plant) => ({
    slug: plant.slug,
    common_name: plant.common_name,
    scientific_name: plant.scientific_name,
  }));

  const requested = params.plant;
  const selected = options.some((plant) => plant.slug === requested)
    ? requested
    : options[0]?.slug;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <header className="max-w-2xl">
        <p className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-accent">
          <Compass className="size-3.5" aria-hidden="true" />
          New assessment
        </p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-foreground">
          Check a location
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          Three steps, and only the first two are required. You will get a comparison of
          every recorded requirement against what the local climate record shows.
        </p>
      </header>

      <div className="mt-8 grid gap-8 lg:grid-cols-[1.6fr_1fr] lg:items-start">
        <section className="rounded-xl border border-border bg-surface p-5 shadow-[var(--shadow)] sm:p-7">
          <AnalysisForm plants={options} initialPlantSlug={selected} />
        </section>

        <aside className="space-y-3">
          {FACTS.map((fact) => (
            <div
              key={fact.title}
              className="rounded-xl border border-border bg-surface-2 p-4"
            >
              <p className="flex items-center gap-2 text-sm font-semibold text-foreground">
                <fact.icon className="size-4 text-primary" aria-hidden="true" />
                {fact.title}
              </p>
              <p className="mt-1.5 text-sm leading-relaxed text-muted">{fact.detail}</p>
            </div>
          ))}
        </aside>
      </div>
    </div>
  );
}
