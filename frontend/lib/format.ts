/**
 * Presentation helpers.
 *
 * Every user-visible string for an enum lives here, so the UI never shows a raw
 * machine value like `partial_sun` or `documented_cultivation`.
 */

import type {
  AssessmentStatus,
  ConfidenceLabel,
  CriterionStatus,
  Difficulty,
  EvidenceType,
  FrostTolerance,
  Lifecycle,
  SunlightRequirement,
  WaterRequirement,
} from "@/types/api";

export const LIFECYCLE_LABEL: Record<Lifecycle, string> = {
  annual: "Annual",
  biennial: "Biennial",
  perennial: "Perennial",
};

export const DIFFICULTY_LABEL: Record<Difficulty, string> = {
  beginner: "Beginner friendly",
  intermediate: "Some experience useful",
  advanced: "For experienced growers",
};

export const WATER_LABEL: Record<WaterRequirement, string> = {
  low: "Low water need",
  moderate: "Moderate water need",
  high: "High water need",
};

export const SUNLIGHT_LABEL: Record<SunlightRequirement, string> = {
  full_sun: "Full sun",
  partial_sun: "Partial sun",
  partial_shade: "Partial shade",
  full_shade: "Full shade",
};

export const FROST_LABEL: Record<FrostTolerance, string> = {
  none: "No frost tolerance",
  light: "Light frost only",
  moderate: "Moderate frost tolerance",
  high: "Hardy to hard frost",
};

export const EVIDENCE_LABEL: Record<EvidenceType, string> = {
  documented_cultivation: "Documented cultivation",
  inferred_suitability: "Modelled inference",
};

export const CRITERION_STATUS_LABEL: Record<CriterionStatus, string> = {
  pass: "Requirement met",
  caution: "Needs attention",
  fail: "Not met",
  unknown: "Not assessed",
};

export const ASSESSMENT_STATUS_LABEL: Record<AssessmentStatus, string> = {
  suitable: "Suitable",
  potentially_suitable: "Potentially suitable",
  not_supported: "Not supported",
  insufficient_data: "Insufficient data",
};

export const CONFIDENCE_LABEL: Record<ConfidenceLabel, string> = {
  high: "High coverage",
  moderate: "Moderate coverage",
  low: "Low coverage",
  none: "No coverage",
};

/** Bordered, soft-background classes for a criterion or assessment status. */
export const STATUS_TONE: Record<CriterionStatus, string> = {
  pass: "border-pass/35 bg-pass-soft text-pass",
  caution: "border-caution/35 bg-caution-soft text-caution",
  fail: "border-fail/35 bg-fail-soft text-fail",
  unknown: "border-unknown/30 bg-unknown-soft text-unknown",
};

export const ASSESSMENT_TONE: Record<AssessmentStatus, string> = {
  suitable: "border-pass/35 bg-pass-soft text-pass",
  potentially_suitable: "border-caution/35 bg-caution-soft text-caution",
  not_supported: "border-fail/35 bg-fail-soft text-fail",
  insufficient_data: "border-unknown/30 bg-unknown-soft text-unknown",
};

/** Left accent bar used on the assessment banner. */
export const ASSESSMENT_BAR: Record<AssessmentStatus, string> = {
  suitable: "bg-pass",
  potentially_suitable: "bg-caution",
  not_supported: "bg-fail",
  insufficient_data: "bg-unknown",
};

export const SOIL_OPTIONS = [
  { value: "loam", label: "Loam" },
  { value: "sandy", label: "Sandy" },
  { value: "clay", label: "Clay" },
  { value: "silt", label: "Silt" },
  { value: "chalky", label: "Chalky" },
] as const;

export const SUNLIGHT_OPTIONS = [
  { value: "full_sun", label: "Full sun (6+ hours)" },
  { value: "partial_sun", label: "Partial sun (3-6 hours)" },
  { value: "partial_shade", label: "Partial shade" },
  { value: "full_shade", label: "Full shade" },
] as const;

export const IRRIGATION_OPTIONS = [
  { value: "none", label: "None, rainfall only" },
  { value: "occasional", label: "Occasional" },
  { value: "regular", label: "Regular" },
  { value: "abundant", label: "Abundant" },
] as const;

export const LIFECYCLE_OPTIONS = [
  { value: "annual", label: "Annual" },
  { value: "biennial", label: "Biennial" },
  { value: "perennial", label: "Perennial" },
] as const;

export const DIFFICULTY_OPTIONS = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
] as const;

/** Format a temperature range, tolerating missing bounds. */
export function formatTemperatureRange(
  min: number | null,
  max: number | null,
): string {
  if (min === null && max === null) return "Not recorded";
  if (min === null) return `up to ${max}\u00a0°C`;
  if (max === null) return `from ${min}\u00a0°C`;
  return `${min}\u2013${max}\u00a0°C`;
}

export function formatNumber(value: number | null, suffix = ""): string {
  if (value === null) return "Not recorded";
  const rounded = Number.isInteger(value) ? value.toFixed(0) : value.toFixed(1);
  return `${rounded}${suffix}`;
}

export function formatCoordinate(value: number): string {
  const hemisphere = value >= 0 ? "N" : "S";
  return `${Math.abs(value).toFixed(4)}° ${hemisphere}`;
}

export function formatCoordinatePair(latitude: number, longitude: number): string {
  const ns = latitude >= 0 ? "N" : "S";
  const ew = longitude >= 0 ? "E" : "W";
  return `${Math.abs(latitude).toFixed(4)}° ${ns}, ${Math.abs(longitude).toFixed(4)}° ${ew}`;
}

const MONTH_NAMES = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

export function monthName(index: number): string {
  return MONTH_NAMES[index - 1] ?? String(index);
}

/** Turn `documented_cultivation` into `Documented cultivation` as a fallback. */
export function humanise(value: string): string {
  const spaced = value.replace(/[_-]+/g, " ").trim();
  return spaced.charAt(0).toUpperCase() + spaced.slice(1);
}
