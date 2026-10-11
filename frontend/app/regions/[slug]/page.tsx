import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, BookOpen, Compass, ExternalLink, Globe, Info, MapPin } from "lucide-react";

import { Notice } from "@/components/feedback";
import { RegionMap } from "@/components/region-map";
import { EVIDENCE_LABEL, formatCoordinatePair } from "@/lib/format";
import { getPlantRegions } from "@/lib/api";

interface PlantRegionsPageProps {
  params: Promise<{ slug: string }>;
}

const MAP_DETAIL =
  "OpenStreetMap contributors. Regions are approximate points of reference, not boundaries.";

export async function generateMetadata({ params }: PlantRegionsPageProps) {
  const { slug } = await params;
  const result = await getPlantRegions(slug);
  if (!result.ok) return { title: "Documented regions" };
  return {
    title: `${result.data.plant.common_name} — documented regions`,
    description: `Places where ${result.data.plant.common_name} is recorded as being cultivated.`,
  };
}

export default async function PlantRegionsPage({ params }: PlantRegionsPageProps) {
  const { slug } = await params;
  const result = await getPlantRegions(slug);

  if (!result.ok) {
    if (result.status === 404) notFound();
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          These regions could not be loaded
        </h1>
        <div className="mt-5">
          <Notice tone="error" title="What happened">
            {result.message}
          </Notice>
        </div>
      </div>
    );
  }

  const { plant, regions, markers, map, notes } = result.data;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
      <nav aria-label="Breadcrumb" className="mb-5 text-sm text-muted">
        <Link href={`/plants/${plant.slug}`} className="hover:text-foreground">
          {plant.common_name}
        </Link>
        <span aria-hidden="true" className="mx-2">
          /
        </span>
        <span className="text-foreground">Documented regions</span>
      </nav>

      <header className="max-w-3xl">
        <p className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-accent">
          <Globe className="size-3.5" aria-hidden="true" />
          Documented cultivation
        </p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-foreground">
          Where {plant.common_name} is grown
        </h1>
        <p className="mt-1 text-sm italic text-muted">{plant.scientific_name}</p>
        <p className="mt-4 text-sm leading-relaxed text-muted">
          Each point is a place with a documented record of this crop being cultivated. Being
          listed here is evidence about the crop, not a verdict on your site — run a site
          check for that.
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <Link
            href={`/location?plant=${encodeURIComponent(plant.slug)}`}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary-hover"
          >
            <Compass className="size-4" aria-hidden="true" />
            Check my own location
          </Link>
          <Link
            href={`/plants/${plant.slug}`}
            className="inline-flex items-center gap-2 rounded-lg border border-border px-4 py-2.5 text-sm font-medium text-foreground hover:bg-surface-2"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to the profile
          </Link>
        </div>
      </header>

      <div className="mt-10 grid gap-8 lg:grid-cols-[1.5fr_1fr] lg:items-start">
        <div>
          <RegionMap markers={markers} config={map} />
          <p className="mt-2 text-xs text-muted">{map.detail || MAP_DETAIL}</p>
        </div>

        <div className="space-y-4">
          {notes.length > 0 ? (
            <div className="rounded-xl border border-border bg-surface-2 p-4">
              <p className="flex items-center gap-2 text-sm font-semibold text-foreground">
                <Info className="size-4 text-muted" aria-hidden="true" />
                About this list
              </p>
              <ul className="mt-2 space-y-2">
                {notes.map((note) => (
                  <li key={note} className="flex gap-2 text-sm leading-relaxed text-muted">
                    <span
                      aria-hidden="true"
                      className="mt-1.5 size-1.5 shrink-0 rounded-full bg-border-strong"
                    />
                    <span>{note}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          <p className="text-sm text-muted">
            {regions.length}{" "}
            {regions.length === 1 ? "region is recorded" : "regions are recorded"} for this
            crop.
          </p>
        </div>
      </div>

      <section aria-labelledby="region-list-heading" className="mt-12">
        <h2
          id="region-list-heading"
          className="flex items-center gap-2 text-xl font-semibold tracking-tight text-foreground"
        >
          <MapPin className="size-5 text-primary" aria-hidden="true" />
          Every recorded region
        </h2>
        <p className="mt-1 text-sm text-muted">
          The list is the authoritative view. Everything plotted on the map appears here.
        </p>

        {regions.length === 0 ? (
          <p className="mt-5 rounded-lg border border-dashed border-border-strong bg-surface p-4 text-sm text-muted">
            No documented cultivation regions are recorded for this crop yet.
          </p>
        ) : (
          <ul className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {regions.map((region) => (
              <li
                key={region.slug}
                className="flex flex-col rounded-xl border border-border bg-surface p-5"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-sm font-semibold text-foreground">{region.name}</h3>
                    <p className="text-xs text-muted">
                      {[region.admin_area, region.country].filter(Boolean).join(", ")}
                    </p>
                  </div>
                  <span className="shrink-0 rounded-full border border-border bg-surface-2 px-2 py-0.5 text-[11px] text-muted">
                    {EVIDENCE_LABEL[region.evidence_type]}
                  </span>
                </div>

                <p className="mt-2 text-xs tabular-nums text-muted">
                  {formatCoordinatePair(region.latitude, region.longitude)}
                </p>

                {region.description ? (
                  <p className="mt-3 flex-1 text-sm leading-relaxed text-muted">
                    {region.description}
                  </p>
                ) : (
                  <p className="flex-1" />
                )}

                {region.climate_note ? (
                  <p className="mt-3 rounded-lg bg-surface-2 px-3 py-2 text-xs leading-relaxed text-muted">
                    {region.climate_note}
                  </p>
                ) : null}

                {region.data_sources.length > 0 ? (
                  <ul className="mt-3 border-t border-border pt-3">
                    {region.data_sources.map((source) => (
                      <li key={`${region.slug}-${source.label}`} className="text-xs">
                        {source.url ? (
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noreferrer noopener"
                            className="inline-flex items-center gap-1 text-primary underline underline-offset-2"
                          >
                            <BookOpen className="size-3" aria-hidden="true" />
                            {source.label}
                            <ExternalLink className="size-3" aria-hidden="true" />
                          </a>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-muted">
                            <BookOpen className="size-3" aria-hidden="true" />
                            {source.label}
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
