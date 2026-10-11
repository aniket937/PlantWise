import Link from "next/link";
import {
  ArrowLeft,
  CircleHelp,
  Compass,
  MapPin,
  RotateCcw,
  Sparkles,
  TriangleAlert,
} from "lucide-react";

import {
  AssessmentPanel,
  CriterionList,
  CultivationEvidencePanel,
  LimitationsList,
  NextStepsList,
} from "@/components/assessment-panel";
import { Notice } from "@/components/feedback";
import { PlantRow } from "@/components/plant-card";
import { postSuitability } from "@/lib/api";

export const metadata = {
  title: "Assessment result",
};

interface ResultsPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

function single(value: string | string[] | undefined): string | undefined {
  if (Array.isArray(value)) return value[0];
  return value;
}

function buildQuery(params: Record<string, string | string[] | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    const one = single(value);
    if (one !== undefined && one !== "") search.set(key, one);
  }
  return search.toString();
}

export default async function ResultsPage({ searchParams }: ResultsPageProps) {
  const params = await searchParams;

  const plantSlug = single(params.plant)?.trim() ?? "";
  const latitude = Number(single(params.lat));
  const longitude = Number(single(params.lon));
  const label = single(params.label)?.trim();
  const explain = single(params.explain) === "1";

  const coordinatesValid =
    single(params.lat) !== undefined &&
    single(params.lon) !== undefined &&
    Number.isFinite(latitude) &&
    Number.isFinite(longitude) &&
    Math.abs(latitude) <= 90 &&
    Math.abs(longitude) <= 180;

  if (!plantSlug || !coordinatesValid) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight text-foreground">
          <CircleHelp className="size-6 text-muted" aria-hidden="true" />
          This assessment link is incomplete
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          A result needs a plant and a valid pair of coordinates. Nothing was evaluated, so
          there is nothing to show here.
        </p>
        <Link
          href="/location"
          className="mt-6 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary-hover"
        >
          <Compass className="size-4" aria-hidden="true" />
          Start a new assessment
        </Link>
      </div>
    );
  }

  const soil = single(params.soil);
  const sunlight = single(params.sun);
  const irrigation = single(params.irrigation);

  const result = await postSuitability(
    {
      plant_slug: plantSlug,
      location: {
        latitude,
        longitude,
        ...(label ? { label } : {}),
        ...(single(params.country) ? { country: single(params.country)! } : {}),
        ...(single(params.cc) ? { country_code: single(params.cc)! } : {}),
        ...(single(params.admin) ? { admin_area: single(params.admin)! } : {}),
        ...(single(params.tz) ? { timezone: single(params.tz)! } : {}),
      },
      ...(soil || sunlight || irrigation
        ? {
            growing_inputs: {
              ...(soil ? { soil_type: soil } : {}),
              ...(sunlight ? { sunlight } : {}),
              ...(irrigation ? { irrigation } : {}),
            },
          }
        : {}),
    },
    { explain },
  );

  const backToForm = `/location?plant=${encodeURIComponent(plantSlug)}`;

  if (!result.ok) {
    const notFound = result.status === 404;
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight text-foreground">
          <TriangleAlert className="size-6 text-fail" aria-hidden="true" />
          {notFound ? "That plant is not in the library" : "The assessment could not be completed"}
        </h1>
        <div className="mt-5">
          <Notice tone={notFound ? "warning" : "error"} title="What happened">
            {result.message}
          </Notice>
        </div>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href={backToForm}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary-hover"
          >
            <RotateCcw className="size-4" aria-hidden="true" />
            Try another plant or place
          </Link>
          <Link
            href="/explore"
            className="inline-flex items-center gap-2 rounded-lg border border-border px-4 py-2.5 text-sm font-medium text-foreground hover:bg-surface-2"
          >
            Browse the library
          </Link>
        </div>
      </div>
    );
  }

  const data = result.data;
  const explainHref = `/results?${buildQuery({ ...params, explain: "1" })}`;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <Link
          href={backToForm}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-muted hover:text-foreground"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Change the plant or location
        </Link>
        <p className="text-xs text-muted">
          Evaluated {new Date(data.evaluated_at).toLocaleString()} · methodology{" "}
          {data.methodology_version}
        </p>
      </div>

      <div className="mb-6 rounded-xl border border-border bg-surface p-5 shadow-[var(--shadow)]">
        <p className="text-xs font-semibold uppercase tracking-wide text-accent">
          Growing suitability
        </p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
          {data.plant.common_name} at {data.location.label}
        </h1>
        <p className="mt-1 text-sm italic text-muted">{data.plant.scientific_name}</p>
        <p className="mt-3 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted">
          <MapPin className="size-3.5" aria-hidden="true" />
          {data.location.latitude.toFixed(4)}, {data.location.longitude.toFixed(4)}
          {data.location.admin_area ? ` · ${data.location.admin_area}` : ""}
          {data.location.country ? ` · ${data.location.country}` : ""}
          {data.location.timezone ? ` · ${data.location.timezone}` : ""}
        </p>
      </div>

      <div className="space-y-10">
        <AssessmentPanel result={data} />

        {data.generated_explanation ? (
          <section aria-labelledby="explain-heading">
            <h2
              id="explain-heading"
              className="flex items-center gap-2 text-xl font-semibold tracking-tight text-foreground"
            >
              <Sparkles className="size-5 text-accent" aria-hidden="true" />
              Plain-language explanation
            </h2>
            <div className="mt-4 rounded-xl border border-border bg-surface p-5">
              {data.generated_explanation.available &&
              data.generated_explanation.text ? (
                <>
                  <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                    {data.generated_explanation.text}
                  </p>
                  <p className="mt-4 border-t border-border pt-3 text-xs text-muted">
                    Written by{" "}
                    <span className="font-medium text-foreground">
                      {data.generated_explanation.model}
                    </span>{" "}
                    served through OpenRouter. It is a restatement of the comparison
                    above and did not change the verdict.
                  </p>
                </>
              ) : (
                <p className="text-sm leading-relaxed text-muted">
                  No written explanation was produced.{" "}
                  {data.generated_explanation.unavailable_reason}
                </p>
              )}
            </div>
          </section>
        ) : (
          <Notice tone="info" title="Want the comparison in plain language?">
            <p>
              A hosted open-weight model can restate the table below in prose. It reads the
              same results and cannot change them.
            </p>
            <Link
              href={explainHref}
              className="mt-3 inline-flex items-center gap-2 rounded-lg border border-border bg-surface px-4 py-2 text-sm font-medium text-foreground hover:bg-surface-2"
            >
              <Sparkles className="size-4" aria-hidden="true" />
              Generate a plain-language explanation
            </Link>
          </Notice>
        )}

        <CriterionList criteria={data.criteria} />

        {data.next_steps.length > 0 ? (
          <NextStepsList steps={data.next_steps} />
        ) : null}

        {data.limitations.length > 0 ? (
          <LimitationsList limitations={data.limitations} />
        ) : null}

        <CultivationEvidencePanel result={data} />

        <section className="rounded-xl border border-border bg-surface-2 p-5">
          <h2 className="text-sm font-semibold text-foreground">The plant assessed</h2>
          <ul className="mt-3">
            <PlantRow plant={data.plant} />
          </ul>
        </section>
      </div>
    </div>
  );
}
