import { BookOpen, ExternalLink, Ruler, Sprout, Timer, TriangleAlert } from "lucide-react";

import {
  FROST_LABEL,
  SUNLIGHT_LABEL,
  WATER_LABEL,
  formatNumber,
  formatTemperatureRange,
  humanise,
} from "@/lib/format";
import type { DataSource, PlantDetail } from "@/types/api";

function Requirement({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail?: string | null;
}) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <dt className="text-xs font-medium uppercase tracking-wide text-muted">{label}</dt>
      <dd className="mt-1.5 text-sm font-semibold text-foreground">{value}</dd>
      {detail ? (
        <p className="mt-2 text-xs leading-relaxed text-muted">{detail}</p>
      ) : null}
    </div>
  );
}

export function RequirementsGrid({ plant }: { plant: PlantDetail }) {
  const { temperature, rainfall, water, sunlight, soil, growing_season } = plant;

  return (
    <section aria-labelledby="requirements-heading">
      <h2
        id="requirements-heading"
        className="flex items-center gap-2 text-xl font-semibold tracking-tight text-foreground"
      >
        <Ruler className="size-5 text-primary" aria-hidden="true" />
        What this plant needs
      </h2>
      <p className="mt-1 max-w-3xl text-sm leading-relaxed text-muted">
        These are the recorded requirements. The suitability check compares them one by one
        against the climate record for a location.
      </p>

      <dl className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Requirement
          label="Temperature range"
          value={formatTemperatureRange(temperature.min_c, temperature.max_c)}
          detail={
            temperature.optimal_min_c !== null && temperature.optimal_max_c !== null
              ? `Optimal ${formatTemperatureRange(temperature.optimal_min_c, temperature.optimal_max_c)}`
              : temperature.notes
          }
        />
        <Requirement
          label="Frost tolerance"
          value={temperature.frost_tolerance ? FROST_LABEL[temperature.frost_tolerance] : "Not recorded"}
        />
        <Requirement
          label="Rainfall"
          value={
            rainfall.min_mm === null && rainfall.max_mm === null
              ? "Not recorded"
              : `${formatNumber(rainfall.min_mm)} – ${formatNumber(rainfall.max_mm)} mm`
          }
          detail={rainfall.notes}
        />
        <Requirement
          label="Water requirement"
          value={water.requirement ? WATER_LABEL[water.requirement] : "Not recorded"}
          detail={water.notes}
        />
        <Requirement
          label="Light"
          value={sunlight.requirement ? SUNLIGHT_LABEL[sunlight.requirement] : "Not recorded"}
          detail={
            sunlight.hours_min !== null
              ? `At least ${sunlight.hours_min} hours of direct light`
              : sunlight.notes
          }
        />
        <Requirement
          label="Soil"
          value={
            soil.textures.length > 0
              ? soil.textures.map(humanise).join(", ")
              : "Not recorded"
          }
          detail={
            soil.ph_min !== null && soil.ph_max !== null
              ? `pH ${soil.ph_min}–${soil.ph_max}${soil.drainage ? ` · ${humanise(soil.drainage)} drainage` : ""}`
              : soil.drainage
                ? `${humanise(soil.drainage)} drainage`
                : soil.notes
          }
        />
        <Requirement
          label="Time to maturity"
          value={
            growing_season.days_min === null && growing_season.days_max === null
              ? "Not recorded"
              : `${formatNumber(growing_season.days_min)} – ${formatNumber(growing_season.days_max)} days`
          }
          detail={growing_season.notes}
        />
      </dl>
    </section>
  );
}

export function CultivationSteps({ steps }: { steps: PlantDetail["cultivation_steps"] }) {
  if (steps.length === 0) return null;

  return (
    <section aria-labelledby="cultivation-heading">
      <h2
        id="cultivation-heading"
        className="flex items-center gap-2 text-xl font-semibold tracking-tight text-foreground"
      >
        <Sprout className="size-5 text-primary" aria-hidden="true" />
        Growing it, step by step
      </h2>

      <ol className="mt-5 space-y-3">
        {steps.map((step) => (
          <li key={step.order} className="flex gap-4 rounded-xl border border-border bg-surface p-5">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-sage text-sm font-semibold tabular-nums text-primary">
              {step.order}
            </span>
            <div>
              <h3 className="text-sm font-semibold text-foreground">{step.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-muted">{step.detail}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}

export function CommonProblems({ problems }: { problems: PlantDetail["common_problems"] }) {
  if (problems.length === 0) return null;

  return (
    <section aria-labelledby="problems-heading">
      <h2
        id="problems-heading"
        className="flex items-center gap-2 text-xl font-semibold tracking-tight text-foreground"
      >
        <TriangleAlert className="size-5 text-caution" aria-hidden="true" />
        What commonly goes wrong
      </h2>

      <ul className="mt-5 grid gap-3 sm:grid-cols-2">
        {problems.map((problem) => (
          <li key={problem.name} className="rounded-xl border border-border bg-surface p-4">
            <h3 className="text-sm font-semibold text-foreground">{problem.name}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-muted">{problem.description}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function SourceList({ sources }: { sources: DataSource[] }) {
  if (sources.length === 0) return null;

  return (
    <section
      aria-labelledby="sources-heading"
      className="rounded-xl border border-border bg-surface-2 p-5"
    >
      <h2
        id="sources-heading"
        className="flex items-center gap-2 text-sm font-semibold text-foreground"
      >
        <BookOpen className="size-4 text-muted" aria-hidden="true" />
        Where this profile comes from
      </h2>
      <ul className="mt-3 space-y-3">
        {sources.map((source) => (
          <li key={`${source.label}-${source.url ?? ""}`} className="text-sm">
            <p className="font-medium text-foreground">{source.label}</p>
            {source.note ? (
              <p className="mt-0.5 text-xs leading-relaxed text-muted">{source.note}</p>
            ) : null}
            {source.url ? (
              <a
                href={source.url}
                target="_blank"
                rel="noreferrer noopener"
                className="mt-1 inline-flex items-center gap-1 text-xs text-primary underline underline-offset-2"
              >
                {source.url.replace(/^https?:\/\//, "").replace(/\/$/, "")}
                <ExternalLink className="size-3" aria-hidden="true" />
              </a>
            ) : null}
          </li>
        ))}
      </ul>
    </section>
  );
}

export function SeasonNote({ note }: { note: string | null }) {
  if (!note) return null;
  return (
    <p className="flex items-start gap-2 rounded-lg border border-border bg-surface px-4 py-3 text-sm leading-relaxed text-muted">
      <Timer className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden="true" />
      {note}
    </p>
  );
}
