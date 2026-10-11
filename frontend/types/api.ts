/**
 * Types mirroring the FastAPI response models.
 *
 * These are hand-written rather than generated so a backend rename becomes a
 * compile error here instead of a silent runtime `undefined`.
 */

export type Lifecycle = "annual" | "biennial" | "perennial";
export type Difficulty = "beginner" | "intermediate" | "advanced";
export type WaterRequirement = "low" | "moderate" | "high";
export type SunlightRequirement =
  | "full_sun"
  | "partial_sun"
  | "partial_shade"
  | "full_shade";
export type FrostTolerance = "none" | "light" | "moderate" | "high";
export type EvidenceType = "documented_cultivation" | "inferred_suitability";

export type CriterionStatus = "pass" | "caution" | "fail" | "unknown";
export type AssessmentStatus =
  | "suitable"
  | "potentially_suitable"
  | "not_supported"
  | "insufficient_data";
export type ConfidenceLabel = "high" | "moderate" | "low" | "none";

export type SoilType = "sandy" | "loam" | "clay" | "silt" | "chalky";
export type IrrigationLevel = "none" | "occasional" | "regular" | "abundant";
export type SunlightInput = SunlightRequirement;

export interface DataSource {
  label: string;
  url: string | null;
  note: string | null;
}

export interface RegionSummary {
  slug: string;
  name: string;
  country: string;
  country_code: string | null;
  admin_area: string | null;
  latitude: number;
  longitude: number;
  evidence_type: EvidenceType;
  description: string | null;
  climate_note: string | null;
  rank: number;
  data_sources: DataSource[];
}

export interface TemperatureProfile {
  min_c: number | null;
  max_c: number | null;
  optimal_min_c: number | null;
  optimal_max_c: number | null;
  frost_tolerance: FrostTolerance | null;
  notes: string | null;
  source: DataSource | null;
}

export interface RainfallProfile {
  min_mm: number | null;
  max_mm: number | null;
  notes: string | null;
  source: DataSource | null;
}

export interface SoilProfile {
  textures: string[];
  ph_min: number | null;
  ph_max: number | null;
  drainage: string | null;
  notes: string | null;
  source: DataSource | null;
}

export interface WaterProfile {
  requirement: WaterRequirement | null;
  notes: string | null;
  source: DataSource | null;
}

export interface SunlightProfile {
  requirement: SunlightRequirement | null;
  hours_min: number | null;
  notes: string | null;
  source: DataSource | null;
}

export interface GrowingSeason {
  days_min: number | null;
  days_max: number | null;
  notes: string | null;
}

export interface CultivationStep {
  order: number;
  title: string;
  detail: string;
}

export interface CommonProblem {
  name: string;
  description: string;
}

export interface PlantSummary {
  slug: string;
  common_name: string;
  scientific_name: string;
  family: string | null;
  short_description: string;
  image_url: string | null;
  image_attribution: string | null;
  image_license: string | null;
  image_source_url: string | null;
  lifecycle: Lifecycle | null;
  growth_habit: string | null;
  difficulty: Difficulty | null;
  tags: string[];
  data_sources: DataSource[];
}

export interface PlantDetail extends PlantSummary {
  description: string | null;
  temperature: TemperatureProfile;
  rainfall: RainfallProfile;
  soil: SoilProfile;
  water: WaterProfile;
  sunlight: SunlightProfile;
  growing_season: GrowingSeason;
  cultivation_steps: CultivationStep[];
  common_problems: CommonProblem[];
  regions: RegionSummary[];
  popularity: number;
}

export interface PlantListResponse {
  items: PlantSummary[];
  total: number;
  query: string | null;
  suggestions: string[];
}

export interface PlantCollection {
  popular: PlantSummary[];
  popular_note: string;
  recent: PlantSummary[];
  recent_note: string;
  total: number;
}

export interface GeocodedLocation {
  label: string;
  name: string;
  latitude: number;
  longitude: number;
  country: string | null;
  country_code: string | null;
  admin_area: string | null;
  admin_area_2: string | null;
  timezone: string | null;
  population: number | null;
  source: string;
}

export interface LocationSearchResponse {
  query: string;
  provider: string;
  results: GeocodedLocation[];
  unavailable_reason: string | null;
}

export interface MonthClimate {
  month: string;
  month_index: number;
  mean_min_c: number;
  mean_max_c: number;
  precipitation_mm: number;
}

export interface MonthExtreme {
  month: string;
  month_index: number;
  value_c: number;
}

export interface ClimateSnapshot {
  available: boolean;
  source: string;
  baseline: string | null;
  latitude: number | null;
  longitude: number | null;
  elevation_m: number | null;
  annual_mean_min_c: number | null;
  annual_mean_max_c: number | null;
  coldest_month: MonthExtreme | null;
  hottest_month: MonthExtreme | null;
  annual_precipitation_mm: number | null;
  frost_days_per_year: number | null;
  growing_degree_days_base10: number | null;
  monthly: MonthClimate[];
  unavailable_reason: string | null;
}

export interface CriterionResult {
  key: string;
  label: string;
  status: CriterionStatus;
  requirement: string;
  observed: string | null;
  explanation: string;
  weight: number;
  source: DataSource | null;
}

export interface Confidence {
  value: number;
  label: ConfidenceLabel;
  evaluated: number;
  total: number;
  methodology: string;
}

export interface Assessment {
  status: AssessmentStatus;
  label: string;
  headline: string;
  summary: string;
  confidence: Confidence;
}

export interface NextStep {
  title: string;
  detail: string;
}

export interface CultivationEvidence {
  available: boolean;
  regions: RegionSummary[];
  note: string;
}

export interface GeneratedExplanation {
  available: boolean;
  model: string | null;
  text: string | null;
  unavailable_reason: string | null;
}

export interface SuitabilityResponse {
  plant: PlantSummary;
  location: {
    label: string;
    latitude: number;
    longitude: number;
    country: string | null;
    country_code: string | null;
    admin_area: string | null;
    timezone: string | null;
    source: string;
  };
  assessment: Assessment;
  climate: ClimateSnapshot;
  criteria: CriterionResult[];
  limitations: string[];
  next_steps: NextStep[];
  cultivation_evidence: CultivationEvidence;
  generated_explanation: GeneratedExplanation | null;
  methodology_version: string;
  evaluated_at: string;
}

export interface MapMarker {
  slug: string;
  name: string;
  country: string;
  latitude: number;
  longitude: number;
  evidence_type: string;
}

export interface RegionMapConfig {
  available: boolean;
  tile_url: string | null;
  attribution: string | null;
  default_center: [number, number];
  default_zoom: number;
  detail: string;
}

export interface PlantRegionsResponse {
  plant: PlantSummary;
  regions: RegionSummary[];
  markers: MapMarker[];
  map: RegionMapConfig;
  notes: string[];
  generated_at: string;
}

export interface RegionPlantOption {
  slug: string;
  common_name: string;
  scientific_name: string;
  image_url: string | null;
  region_count: number;
}

export interface RegionPlantListResponse {
  items: RegionPlantOption[];
}

export interface AssistantStatusResponse {
  available: boolean;
  model: string;
  base_url_configured: boolean;
  detail: string;
  checked_at: string;
}

export interface AssistantContext {
  plant_slug: string | null;
  plant_common_name: string | null;
  plant_scientific_name: string | null;
  location_label: string | null;
  applied: boolean;
}

export interface AssistantChatResponse {
  available: boolean;
  reply: string | null;
  model: string;
  unavailable_reason: string | null;
  disclaimer: string;
  context: AssistantContext;
  latency_ms: number | null;
}

export interface HealthResponse {
  status: "ok" | "degraded";
  app: string;
  version: string;
  environment: string;
  capabilities: Record<
    string,
    { available: boolean; detail: string; model?: string }
  >;
  database: { available: boolean; detail: string };
}

export interface ErrorPayload {
  error: {
    code: string;
    message: string;
    details: { field: string | null; message: string }[] | null;
  };
}
