import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  Compass,
  Gauge,
  Info,
  Lightbulb,
  ListChecks,
  MapPin,
  ShieldCheck,
} from "lucide-react";

import { StatusBadge } from "@/components/status-badge";
import {
  ASSESSMENT_BAR,
  ASSESSMENT_TONE,
  ASSESSMENT_STATUS_LABEL,
  CONFIDENCE_LABEL,
  EVIDENCE_LABEL,
  monthName,
} from "@/lib/format";
import type { SuitabilityResponse } from "@/types/api";

function Stat({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-surface p-3">
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="mt-1 text-sm font-semibold text-foreground">{value}</dd>
      {hint ? <p className="mt-1 text-xs text-muted">{hint}</p> : null}
    </div>
  );
}

/** The headline verdict. Never a percentage; a status plus coverage. */
export function AssessmentPanel({ result }: { result: SuitabilityResponse }) {
  const { assessment, climate, location, criteria } = result;
  const passed = criteria.filter((item) => item.status === "pass").length;
  const needsAttention = criteria.filter((item) => item.status === "caution").length;
  const failed = criteria.filter((item) => item.status === "fail").length;
  const notAssessed = criteria.filter((item) => item.status === "unknown").length;

  return (
    <section aria-labelledby="assessment-heading" className="space-y-4">
      <div
        className={`overflow-hidden rounded-xl border bg-surface shadow-[var(--shadow)] ${ASSESSMENT_TONE[assessment.status]}`}
      >
        <div className="flex">
          <div className={`w-1.5 shrink-0 ${ASSESSMENT_BAR[assessment.status]}`} />
          <div className="flex-1 p-5 sm:p-6">
            <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide">
              <ShieldCheck className="size-4" aria-hidden="true" />
              {ASSESSMENT_STATUS_LABEL[assessment.status]}
            </p>
            <h2
              id="assessment-heading"
              className="mt-2 text-lg font-semibold leading-snug text-foreground sm:text-xl"
            >
              {assessment.headline}
            </h2>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-foreground/85">
              {assessment.summary}
            </p>

            <p className="mt-4 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-foreground/80">
              <MapPin className="size-3.5" aria-hidden="true" />
              <span className="font-medium">{location.label}</span>
              <span aria-hidden="true">·</span>
              <span>
                {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
              </span>
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Stat
          label="Criteria met"
          value={`${passed} of ${criteria.length}`}
          hint={failed > 0 ? `${failed} not met` : "No hard requirement failed"}
        />
        <Stat
          label="Needing attention"
          value={String(needsAttention)}
          hint={needsAttention > 0 ? "Workable with adjustments" : "Nothing flagged"}
        />
        <Stat
          label="Evidence coverage"
          value={`${Math.round(assessment.confidence.value * 100)}%`}
          hint={`${assessment.confidence.evaluated} of ${assessment.confidence.total} criteria assessed`}
        />
        <Stat
          label="Not assessed"
          value={String(notAssessed)}
          hint={notAssessed > 0 ? "Missing inputs, see limitations" : "All criteria assessed"}
        />
      </div>

      <ConfidenceNote result={result} />
      {climate.available ? <ClimateSummary result={result} /> : null}
    </section>
  );
}

function ConfidenceNote({ result }: { result: SuitabilityResponse }) {
  const { confidence } = result.assessment;
  return (
    <div className="flex gap-3 rounded-lg border border-border bg-surface-2 p-4">
      <Gauge className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden="true" />
      <div className="text-sm">
        <p className="font-medium text-foreground">
          Confidence: {confidence.label} ({CONFIDENCE_LABEL[confidence.label]})
        </p>
        <p className="mt-1 leading-relaxed text-muted">{confidence.methodology}</p>
      </div>
    </div>
  );
}

function ClimateSummary({ result }: { result: SuitabilityResponse }) {
  const { climate } = result;
  return (
    <div className="rounded-xl border border-border bg-surface p-5">
      <h3 className="flex items-center gap-2 text-sm font-semibold text-foreground">
        <Compass className="size-4 text-muted" aria-hidden="true" />
        What this was compared against
      </h3>
      <p className="mt-1 text-xs text-muted">
        {climate.source}
        {climate.baseline ? `, baseline ${climate.baseline}` : ""}
        {climate.elevation_m !== null ? `, elevation about ${Math.round(climate.elevation_m)} m` : ""}
      </p>

      <dl className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Stat
          label="Coldest month (mean minimum)"
          value={
            climate.coldest_month
              ? `${climate.coldest_month.value_c}\u00a0°C`
              : "Not available"
          }
          hint={climate.coldest_month ? monthName(climate.coldest_month.month_index) : undefined}
        />
        <Stat
          label="Hottest month (mean maximum)"
          value={
            climate.hottest_month
              ? `${climate.hottest_month.value_c}\u00a0°C`
              : "Not available"
          }
          hint={climate.hottest_month ? monthName(climate.hottest_month.month_index) : undefined}
        />
        <Stat
          label="Annual precipitation"
          value={
            climate.annual_precipitation_mm !== null
              ? `${Math.round(climate.annual_precipitation_mm)}\u00a0mm`
              : "Not available"
          }
        />
        <Stat
          label="Frost days per year"
          value={climate.frost_days_per_year !== null ? String(climate.frost_days_per_year) : "Not available"}
          hint="Days with a minimum below 0 °C"
        />
      </dl>
    </div>
  );
}

/** Every criterion, showing requirement, observation and reasoning. */
export function CriterionList({ criteria }: { criteria: SuitabilityResponse["criteria"] }) {
  return (
    <section aria-labelledby="criteria-heading" className="space-y-4">
      <div>
        <h2 id="criteria-heading" className="text-xl font-semibold tracking-tight text-foreground">
          What was compared
        </h2>
        <p className="mt-1 max-w-3xl text-sm leading-relaxed text-muted">
          Each row puts one published requirement for this plant next to what the local
          climate record actually shows. A criterion marked as not assessed had no data to
          compare, so it is excluded from the verdict rather than assumed to pass.
        </p>
      </div>

      <ul className="space-y-3">
        {criteria.map((criterion) => (
          <li key={criterion.key} className="rounded-xl border border-border bg-surface p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <h3 className="text-sm font-semibold text-foreground">{criterion.label}</h3>
              <StatusBadge status={criterion.status} />
            </div>

            <dl className="mt-3 grid gap-3 sm:grid-cols-2">
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted">
                  Requirement
                </dt>
                <dd className="mt-1 text-sm text-foreground">{criterion.requirement}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted">
                  Observed here
                </dt>
                <dd className="mt-1 text-sm text-foreground">
                  {criterion.observed ?? "No data available"}
                </dd>
              </div>
            </dl>

            <p className="mt-3 text-sm leading-relaxed text-muted">{criterion.explanation}</p>

            {criterion.source ? (
              <p className="mt-3 flex flex-wrap items-center gap-1.5 text-xs text-muted">
                <BookOpen className="size-3.5" aria-hidden="true" />
                <span>Requirement source: {criterion.source.label}</span>
                {criterion.source.url ? (
                  <a
                    href={criterion.source.url}
                    className="text-primary underline underline-offset-2"
                    target="_blank"
                    rel="noreferrer noopener"
                  >
                    open reference
                  </a>
                ) : null}
              </p>
            ) : null}
          </li>
        ))}
      </ul>
    </section>
  );
}

export function NextStepsList({ steps }: { steps: SuitabilityResponse["next_steps"] }) {
  return (
    <section aria-labelledby="next-steps-heading" className="space-y-4">
      <h2
        id="next-steps-heading"
        className="flex items-center gap-2 text-xl font-semibold tracking-tight text-foreground"
      >
        <ListChecks className="size-5 text-primary" aria-hidden="true" />
        What to do next
      </h2>
      <ul className="grid gap-3 sm:grid-cols-2">
        {steps.map((step, index) => (
          <li key={step.title} className="rounded-xl border border-border bg-surface p-4">
            <p className="flex items-baseline gap-2 text-sm font-semibold text-foreground">
              <span className="text-xs tabular-nums text-accent">
                {String(index + 1).padStart(2, "0")}
              </span>
              {step.title}
            </p>
            <p className="mt-2 text-sm leading-relaxed text-muted">{step.detail}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function LimitationsList({ limitations }: { limitations: string[] }) {
  return (
    <section
      aria-labelledby="limitations-heading"
      className="rounded-xl border border-border bg-surface-2 p-5"
    >
      <h2
        id="limitations-heading"
        className="flex items-center gap-2 text-sm font-semibold text-foreground"
      >
        <Info className="size-4 text-muted" aria-hidden="true" />
        Limitations of this assessment
      </h2>
      <ul className="mt-3 space-y-2">
        {limitations.map((limitation) => (
          <li key={limitation} className="flex gap-2 text-sm leading-relaxed text-muted">
            <span aria-hidden="true" className="mt-1.5 size-1.5 shrink-0 rounded-full bg-border-strong" />
            <span>{limitation}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Documented cultivation evidence, kept visually and verbally separate from the
 * environmental verdict so the two can never be confused.
 */
export function CultivationEvidencePanel({
  result,
}: {
  result: SuitabilityResponse;
}) {
  const { cultivation_evidence: evidence, plant } = result;

  return (
    <section aria-labelledby="evidence-heading" className="space-y-4">
      <div>
        <h2
          id="evidence-heading"
          className="flex items-center gap-2 text-xl font-semibold tracking-tight text-foreground"
        >
          <Lightbulb className="size-5 text-accent" aria-hidden="true" />
          Where this crop is known to be grown
        </h2>
        <p className="mt-1 max-w-3xl text-sm leading-relaxed text-muted">{evidence.note}</p>
      </div>

      {evidence.available ? (
        <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {evidence.regions.slice(0, 6).map((region) => (
            <li key={region.slug} className="rounded-xl border border-border bg-surface p-4">
              <p className="text-sm font-semibold text-foreground">{region.name}</p>
              <p className="text-xs text-muted">
                {[region.admin_area, region.country].filter(Boolean).join(", ")}
              </p>
              <p className="mt-2 text-xs font-medium text-accent">
                {EVIDENCE_LABEL[region.evidence_type]}
              </p>
              {region.description ? (
                <p className="mt-2 line-clamp-3 text-xs leading-relaxed text-muted">
                  {region.description}
                </p>
              ) : null}
            </li>
          ))}
        </ul>
      ) : (
        <p className="rounded-lg border border-dashed border-border-strong bg-surface p-4 text-sm text-muted">
          No documented cultivation areas are recorded for this crop yet.
        </p>
      )}

      <Link
        href={`/regions/${plant.slug}`}
        className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 text-sm font-medium text-foreground hover:bg-surface-2"
      >
        See all documented regions for {plant.common_name}
        <ArrowRight className="size-4" aria-hidden="true" />
      </Link>
    </section>
  );
}
