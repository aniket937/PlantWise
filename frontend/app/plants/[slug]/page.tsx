import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowRight,
  Compass,
  ExternalLink,
  Leaf,
  MapPin,
  MessageCircle,
  Sprout,
  Wheat,
} from "lucide-react";

import { Notice } from "@/components/feedback";
import { PlantImage } from "@/components/plant-image";
import {
  CommonProblems,
  CultivationSteps,
  RequirementsGrid,
  SourceList,
} from "@/components/plant-profile-sections";
import { RegionMap } from "@/components/region-map";
import { DIFFICULTY_LABEL, EVIDENCE_LABEL, LIFECYCLE_LABEL } from "@/lib/format";
import { getPlant, getPlantRegions } from "@/lib/api";

interface PlantPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: PlantPageProps) {
  const { slug } = await params;
  const result = await getPlant(slug);
  if (!result.ok) return { title: "Plant profile" };
  return {
    title: result.data.common_name,
    description: result.data.short_description,
  };
}

export default async function PlantPage({ params }: PlantPageProps) {
  const { slug } = await params;
  const result = await getPlant(slug);

  if (!result.ok) {
    if (result.status === 404) notFound();
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          This profile could not be loaded
        </h1>
        <div className="mt-5">
          <Notice tone="error" title="What happened">
            {result.message}
          </Notice>
        </div>
      </div>
    );
  }

  const plant = result.data;
  const regions = await getPlantRegions(slug);

  const facts = [
    { label: "Botanical family", value: plant.family },
    {
      label: "Lifecycle",
      value: plant.lifecycle ? LIFECYCLE_LABEL[plant.lifecycle] : null,
    },
    { label: "Growth habit", value: plant.growth_habit },
    {
      label: "Difficulty",
      value: plant.difficulty ? DIFFICULTY_LABEL[plant.difficulty] : null,
    },
  ].filter((fact) => Boolean(fact.value));

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
      <nav aria-label="Breadcrumb" className="mb-5 text-sm text-muted">
        <Link href="/explore" className="hover:text-foreground">
          Plant library
        </Link>
        <span aria-hidden="true" className="mx-2">
          /
        </span>
        <span className="text-foreground">{plant.common_name}</span>
      </nav>

      <header className="grid gap-8 lg:grid-cols-[1fr_1.4fr] lg:items-start">
        <div className="overflow-hidden rounded-xl border border-border bg-surface">
          <PlantImage
            src={plant.image_url}
            alt={plant.common_name}
            aspectClassName="aspect-[4/3]"
            sizes="(min-width: 1024px) 420px, 90vw"
            preload
          />
          {plant.image_attribution ? (
            <div className="border-t border-border p-3 text-xs text-muted">
              <p>
                Photo: {plant.image_attribution}
                {plant.image_license ? ` · ${plant.image_license}` : ""}
              </p>
              {plant.image_source_url ? (
                <a
                  href={plant.image_source_url}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="mt-1 inline-flex items-center gap-1 text-primary underline underline-offset-2"
                >
                  View the original file
                  <ExternalLink className="size-3" aria-hidden="true" />
                </a>
              ) : null}
            </div>
          ) : null}
        </div>

        <div>
          <p className="inline-flex items-center gap-2 rounded-full border border-border bg-sage px-3 py-1 text-xs font-medium text-foreground">
            <Leaf className="size-3.5" aria-hidden="true" />
            Growing profile
          </p>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            {plant.common_name}
          </h1>
          <p className="mt-1 text-base italic text-muted">{plant.scientific_name}</p>

          <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted">
            {plant.description ?? plant.short_description}
          </p>

          {plant.tags.length > 0 ? (
            <ul className="mt-4 flex flex-wrap gap-2">
              {plant.tags.map((tag) => (
                <li
                  key={tag}
                  className="rounded-full border border-border bg-surface-2 px-2.5 py-1 text-xs text-muted"
                >
                  {tag}
                </li>
              ))}
            </ul>
          ) : null}

          {facts.length > 0 ? (
            <dl className="mt-6 grid gap-3 sm:grid-cols-2">
              {facts.map((fact) => (
                <div key={fact.label} className="rounded-lg border border-border bg-surface p-3">
                  <dt className="text-xs text-muted">{fact.label}</dt>
                  <dd className="mt-1 text-sm font-medium text-foreground">{fact.value}</dd>
                </div>
              ))}
            </dl>
          ) : null}

          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href={`/location?plant=${encodeURIComponent(plant.slug)}`}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-medium text-primary-foreground hover:bg-primary-hover"
            >
              <Compass className="size-4" aria-hidden="true" />
              Check a location for this plant
            </Link>
            <Link
              href={`/assistant?plant=${encodeURIComponent(plant.slug)}`}
              className="inline-flex items-center gap-2 rounded-lg border border-border px-5 py-3 text-sm font-medium text-foreground hover:bg-surface-2"
            >
              <MessageCircle className="size-4" aria-hidden="true" />
              Ask about growing it
            </Link>
          </div>
        </div>
      </header>

      <div className="mt-12 space-y-12">
        <RequirementsGrid plant={plant} />

        <CultivationSteps steps={plant.cultivation_steps} />

        <CommonProblems problems={plant.common_problems} />

        <section aria-labelledby="regions-heading">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2
                id="regions-heading"
                className="flex items-center gap-2 text-xl font-semibold tracking-tight text-foreground"
              >
                <MapPin className="size-5 text-primary" aria-hidden="true" />
                Where this crop is documented
              </h2>
              <p className="mt-1 max-w-3xl text-sm leading-relaxed text-muted">
                These are places the crop is recorded as being cultivated, not places this
                tool has judged to be suitable. The two are different claims.
              </p>
            </div>
            <Link
              href={`/regions/${plant.slug}`}
              className="inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline"
            >
              Open the full region view
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
          </div>

          {regions.ok && regions.data.regions.length > 0 ? (
            <>
              <div className="mt-5">
                <RegionMap markers={regions.data.markers} config={regions.data.map} />
              </div>
              <ul className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {regions.data.regions.slice(0, 6).map((region) => (
                  <li key={region.slug} className="rounded-xl border border-border bg-surface p-4">
                    <p className="text-sm font-semibold text-foreground">{region.name}</p>
                    <p className="text-xs text-muted">
                      {[region.admin_area, region.country].filter(Boolean).join(", ")}
                    </p>
                    <p className="mt-2 text-xs font-medium text-accent">
                      {EVIDENCE_LABEL[region.evidence_type]}
                    </p>
                    {region.climate_note ? (
                      <p className="mt-2 text-xs leading-relaxed text-muted">
                        {region.climate_note}
                      </p>
                    ) : null}
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p className="mt-5 rounded-lg border border-dashed border-border-strong bg-surface p-4 text-sm text-muted">
              {regions.ok
                ? "No documented cultivation regions are recorded for this crop yet."
                : regions.message}
            </p>
          )}
        </section>

        {plant.growing_season.notes ? (
          <section className="rounded-xl border border-border bg-surface p-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <Wheat className="size-4 text-accent" aria-hidden="true" />
              Season notes
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-muted">
              {plant.growing_season.notes}
            </p>
          </section>
        ) : null}

        <SourceList sources={plant.data_sources} />

        <section className="rounded-xl border border-border bg-surface-2 p-5">
          <h2 className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <Sprout className="size-4 text-primary" aria-hidden="true" />
            Keep in mind
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-relaxed text-muted">
            This profile records published requirements for the species in general. Cultivar,
            soil depth, drainage, shelter and local management all affect real outcomes, and
            none of them are captured here. Treat a suitability result as a starting point for
            local advice, not a conclusion.
          </p>
        </section>
      </div>
    </div>
  );
}
