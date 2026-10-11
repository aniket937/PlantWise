import Link from "next/link";
import {
  ArrowRight,
  Compass,
  ListChecks,
  MapPin,
  Search,
  ShieldCheck,
  Sprout,
} from "lucide-react";

import { Notice } from "@/components/feedback";
import { PlantCard } from "@/components/plant-card";
import { SectionHeading } from "@/components/section-heading";
import { getFeaturedPlants, getPlants } from "@/lib/api";

export const metadata = {
  title: "PlantWise AI — what grows well where you are",
};

const STEPS = [
  {
    icon: Search,
    title: "Find a plant",
    detail:
      "Browse sourced growing profiles with the temperature, water, soil and light each crop actually needs.",
  },
  {
    icon: MapPin,
    title: "Choose a place",
    detail:
      "Search for a town, or drop in coordinates. Climate comes from a ten-year daily reanalysis baseline.",
  },
  {
    icon: ListChecks,
    title: "See how they compare",
    detail:
      "Every requirement is listed next to what the local record shows, with the reasoning and the gaps named.",
  },
] as const;

export default async function HomePage() {
  const [featured, browse] = await Promise.all([
    getFeaturedPlants(),
    getPlants({ limit: 6 }),
  ]);

  const backendDown = !featured.ok && !browse.ok;
  const collection = featured.ok ? featured.data : null;
  const fallbackPlants = browse.ok ? browse.data.items : [];

  const popular =
    collection && collection.popular.length > 0 ? collection.popular : fallbackPlants;
  const popularNote =
    collection && collection.popular.length > 0
      ? collection.popular_note
      : "A selection from the plant library.";
  const recent = collection?.recent ?? [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <section className="grid gap-10 lg:grid-cols-[1.1fr_1fr] lg:items-center">
        <div>
          <p className="inline-flex items-center gap-2 rounded-full border border-border bg-sage px-3 py-1 text-xs font-medium text-foreground">
            <Sprout className="size-3.5" aria-hidden="true" />
            Plant discovery and growing suitability
          </p>
          <h1 className="mt-5 text-3xl font-semibold leading-tight tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            Understand what will actually grow where you are.
          </h1>
          <p className="mt-5 max-w-xl text-base leading-relaxed text-muted">
            PlantWise compares the documented requirements of a crop against long-term
            climate records for a specific place. You get the comparison itself — each
            requirement beside the observed local value — rather than an unexplained score.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/location"
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-medium text-primary-foreground hover:bg-primary-hover"
            >
              <Compass className="size-4" aria-hidden="true" />
              Check a location
            </Link>
            <Link
              href="/explore"
              className="inline-flex items-center gap-2 rounded-lg border border-border px-5 py-3 text-sm font-medium text-foreground hover:bg-surface-2"
            >
              Explore the plant library
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
          </div>

          <p className="mt-5 flex items-start gap-2 text-xs leading-relaxed text-muted">
            <ShieldCheck className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            Suitability is computed by a documented rule engine. The AI assistant can
            explain a result, but it never decides it.
          </p>
        </div>

        <ol className="grid gap-3">
          {STEPS.map((step, index) => (
            <li
              key={step.title}
              className="flex gap-4 rounded-xl border border-border bg-surface p-4 shadow-[var(--shadow)]"
            >
              <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-sage text-primary">
                <step.icon className="size-4.5" aria-hidden="true" />
              </span>
              <div>
                <p className="flex items-baseline gap-2 text-sm font-semibold text-foreground">
                  <span className="text-xs tabular-nums text-accent">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  {step.title}
                </p>
                <p className="mt-1 text-sm leading-relaxed text-muted">{step.detail}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      {backendDown ? (
        <div className="mt-10">
          <Notice tone="warning" title="The plant library could not be loaded">
            {featured.message} Start the backend with{" "}
            <code className="rounded bg-surface-2 px-1.5 py-0.5 text-xs">
              uvicorn app.main:app --reload
            </code>{" "}
            from the <code className="text-xs">backend</code> directory, then reload this
            page.
          </Notice>
        </div>
      ) : null}

      {popular.length > 0 ? (
        <section className="mt-14" aria-labelledby="popular-heading">
          <SectionHeading
            eyebrow="Plant library"
            id="popular-heading"
            title="Start with these"
            description={popularNote}
            action={
              <Link
                href="/explore"
                className="inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline"
              >
                Browse all plants
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
            }
          />
          <ul className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {popular.slice(0, 6).map((plant, index) => (
              <li key={plant.slug}>
                <PlantCard plant={plant} preload={index === 0} />
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {recent.length > 0 ? (
        <section className="mt-14" aria-labelledby="recent-heading">
          <SectionHeading
            id="recent-heading"
            title="Recently viewed"
            description={collection?.recent_note}
          />
          <ul className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {recent.slice(0, 3).map((plant) => (
              <li key={plant.slug}>
                <PlantCard plant={plant} />
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="mt-16 rounded-xl border border-border bg-surface-2 p-6 sm:p-8">
        <h2 className="text-lg font-semibold tracking-tight text-foreground">
          What this does, and what it does not
        </h2>
        <div className="mt-5 grid gap-6 sm:grid-cols-2">
          <div>
            <h3 className="text-sm font-semibold text-foreground">It does</h3>
            <ul className="mt-2 space-y-2 text-sm leading-relaxed text-muted">
              <li>
                Compare published crop requirements against multi-year climate normals for a
                specific coordinate.
              </li>
              <li>
                Show each comparison in full, including which requirements could not be
                assessed and why.
              </li>
              <li>
                Separate <em>documented cultivation</em> — places the crop is known to be
                grown — from an assessment of your own site.
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">It does not</h3>
            <ul className="mt-2 space-y-2 text-sm leading-relaxed text-muted">
              <li>Produce a suitability percentage, or predict a yield or a profit.</li>
              <li>
                Model pests, disease, drainage in practice, cultivar choice or market
                access.
              </li>
              <li>
                Replace local knowledge. Confirm important decisions with an agronomist or
                extension service.
              </li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}
