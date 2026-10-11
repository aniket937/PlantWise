/**
 * Server-side API client.
 *
 * Every call returns a discriminated result instead of throwing, so a page can
 * render an honest "the backend is not reachable" state rather than crashing or
 * inventing data.
 */

import type {
  AssistantChatResponse,
  AssistantStatusResponse,
  ErrorPayload,
  HealthResponse,
  LocationSearchResponse,
  PlantCollection,
  PlantDetail,
  PlantListResponse,
  PlantRegionsResponse,
  RegionPlantListResponse,
  SuitabilityResponse,
} from "@/types/api";

export const API_BASE_URL = (
  process.env.PLANTWISE_API_URL ?? "http://127.0.0.1:8000"
).replace(/\/+$/, "");

const API_PREFIX = "/api/v1";

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; status: number; message: string; code: string };

function looksLikeErrorPayload(value: unknown): value is ErrorPayload {
  if (typeof value !== "object" || value === null) return false;
  const candidate = value as { error?: unknown };
  return typeof candidate.error === "object" && candidate.error !== null;
}

async function readMessage(response: Response): Promise<{ message: string; code: string }> {
  try {
    const body: unknown = await response.json();
    if (looksLikeErrorPayload(body)) {
      return { message: body.error.message, code: body.error.code };
    }
    return { message: `Request failed with status ${response.status}.`, code: "unknown" };
  } catch {
    return { message: `Request failed with status ${response.status}.`, code: "unknown" };
  }
}

async function request<T>(
  path: string,
  init?: RequestInit & { timeoutMs?: number },
): Promise<ApiResult<T>> {
  const { timeoutMs = 20000, ...rest } = init ?? {};
  const url = `${API_BASE_URL}${API_PREFIX}${path}`;
  try {
    const response = await fetch(url, {
      ...rest,
      // Climate lookups must never be cached stale in the app layer.
      cache: "no-store",
      headers: { Accept: "application/json", ...(rest.headers ?? {}) },
      signal: AbortSignal.timeout(timeoutMs),
    });
    if (!response.ok) {
      const { message, code } = await readMessage(response);
      return { ok: false, status: response.status, message, code };
    }
    return { ok: true, data: (await response.json()) as T };
  } catch (error) {
    const timedOut = error instanceof DOMException && error.name === "TimeoutError";
    return {
      ok: false,
      status: 0,
      code: timedOut ? "timeout" : "unreachable",
      message: timedOut
        ? "The PlantWise API did not respond in time."
        : "The PlantWise API could not be reached. Check that the backend is running.",
    };
  }
}

function queryString(params: Record<string, unknown>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    search.set(key, String(value));
  }
  const encoded = search.toString();
  return encoded ? `?${encoded}` : "";
}

/* ------------------------------------------------------------------ health */

export function getHealth(): Promise<ApiResult<HealthResponse>> {
  return request<HealthResponse>("/health", { timeoutMs: 8000 });
}

/* ------------------------------------------------------------------ plants */

export type PlantQuery = {
  query?: string;
  lifecycle?: string;
  difficulty?: string;
  tag?: string;
  limit?: number;
  offset?: number;
};

export function getPlants(query: PlantQuery = {}): Promise<ApiResult<PlantListResponse>> {
  return request<PlantListResponse>(`/plants${queryString(query)}`);
}

export function getPlant(slug: string): Promise<ApiResult<PlantDetail>> {
  return request<PlantDetail>(`/plants/${encodeURIComponent(slug)}`);
}

export function getFeaturedPlants(): Promise<ApiResult<PlantCollection>> {
  return request<PlantCollection>("/plants/featured", { timeoutMs: 10000 });
}

/* --------------------------------------------------------------- locations */

export function searchLocations(
  query: string,
  limit = 6,
): Promise<ApiResult<LocationSearchResponse>> {
  return request<LocationSearchResponse>(
    `/locations/search${queryString({ q: query, limit })}`,
    { timeoutMs: 12000 },
  );
}

/* ------------------------------------------------------------- suitability */

export interface SuitabilityRequestBody {
  plant_slug: string;
  location?: {
    latitude: number;
    longitude: number;
    label?: string;
    name?: string;
    country?: string;
    country_code?: string;
    admin_area?: string;
    timezone?: string;
  };
  place_query?: string;
  growing_inputs?: {
    soil_type?: string;
    sunlight?: string;
    irrigation?: string;
  };
}

export function postSuitability(
  body: SuitabilityRequestBody,
  options: { explain?: boolean } = {},
): Promise<ApiResult<SuitabilityResponse>> {
  return request<SuitabilityResponse>(
    `/suitability${queryString({ explain: options.explain ? "true" : undefined })}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      timeoutMs: options.explain ? 150000 : 45000,
    },
  );
}

/* ----------------------------------------------------------------- regions */

export function getPlantsWithRegions(): Promise<ApiResult<RegionPlantListResponse>> {
  return request<RegionPlantListResponse>("/regions/plants");
}

export function getPlantRegions(slug: string): Promise<ApiResult<PlantRegionsResponse>> {
  return request<PlantRegionsResponse>(`/regions/${encodeURIComponent(slug)}`);
}

/* --------------------------------------------------------------- assistant */

export function getAssistantStatus(): Promise<ApiResult<AssistantStatusResponse>> {
  return request<AssistantStatusResponse>("/assistant/status", { timeoutMs: 8000 });
}

export interface ChatMessageInput {
  role: "user" | "assistant";
  content: string;
}

export function postAssistantChat(body: {
  messages: ChatMessageInput[];
  plant_slug?: string;
  location?: SuitabilityRequestBody["location"];
}): Promise<ApiResult<AssistantChatResponse>> {
  return request<AssistantChatResponse>("/assistant/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    timeoutMs: 150000,
  });
}
