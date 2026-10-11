"use client";

import { useRouter } from "next/navigation";
import { Crosshair, LoaderCircle, Sprout, TriangleAlert } from "lucide-react";
import { useMemo, useState } from "react";

import { LocationAutocomplete } from "@/components/location-autocomplete";
import {
  IRRIGATION_OPTIONS,
  SOIL_OPTIONS,
  SUNLIGHT_OPTIONS,
} from "@/lib/format";
import type { GeocodedLocation, PlantSummary } from "@/types/api";

interface AnalysisFormProps {
  plants: Pick<PlantSummary, "slug" | "common_name" | "scientific_name">[];
  initialPlantSlug?: string;
}

const selectClasses =
  "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-foreground";

export function AnalysisForm({ plants, initialPlantSlug }: AnalysisFormProps) {
  const router = useRouter();
  const [plantSlug, setPlantSlug] = useState(
    initialPlantSlug ?? plants[0]?.slug ?? "",
  );
  const [location, setLocation] = useState<GeocodedLocation | null>(null);
  const [manual, setManual] = useState(false);
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [soil, setSoil] = useState("");
  const [sunlight, setSunlight] = useState("");
  const [irrigation, setIrrigation] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const parsedCoordinates = useMemo(() => {
    const lat = Number(latitude);
    const lon = Number(longitude);
    const validLat = latitude.trim() !== "" && Number.isFinite(lat) && Math.abs(lat) <= 90;
    const validLon = longitude.trim() !== "" && Number.isFinite(lon) && Math.abs(lon) <= 180;
    return { lat, lon, validLat, validLon };
  }, [latitude, longitude]);

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!plantSlug) {
      setError("Choose a plant to assess.");
      return;
    }

    const params = new URLSearchParams({ plant: plantSlug });

    if (manual) {
      if (!parsedCoordinates.validLat || !parsedCoordinates.validLon) {
        setError(
          "Enter a latitude between -90 and 90 and a longitude between -180 and 180.",
        );
        return;
      }
      params.set("lat", String(parsedCoordinates.lat));
      params.set("lon", String(parsedCoordinates.lon));
      params.set("label", `${parsedCoordinates.lat.toFixed(4)}, ${parsedCoordinates.lon.toFixed(4)}`);
    } else {
      if (!location) {
        setError("Search for a place, or switch to entering coordinates directly.");
        return;
      }
      params.set("lat", String(location.latitude));
      params.set("lon", String(location.longitude));
      params.set("label", location.label);
      if (location.country) params.set("country", location.country);
      if (location.country_code) params.set("cc", location.country_code);
      if (location.admin_area) params.set("admin", location.admin_area);
      if (location.timezone) params.set("tz", location.timezone);
    }

    if (soil) params.set("soil", soil);
    if (sunlight) params.set("sun", sunlight);
    if (irrigation) params.set("irrigation", irrigation);

    setPending(true);
    router.push(`/results?${params.toString()}`);
  }

  return (
    <form onSubmit={submit} className="space-y-6" noValidate>
      <fieldset className="space-y-4" disabled={pending}>
        <legend className="text-lg font-semibold tracking-tight text-foreground">
          Step 1. Choose a plant
        </legend>

        <div className="space-y-2">
          <label htmlFor="plant" className="block text-sm font-medium text-foreground">
            Plant profile
          </label>
          <select
            id="plant"
            value={plantSlug}
            onChange={(event) => setPlantSlug(event.target.value)}
            className={selectClasses}
          >
            {plants.map((plant) => (
              <option key={plant.slug} value={plant.slug}>
                {plant.common_name} ({plant.scientific_name})
              </option>
            ))}
          </select>
        </div>
      </fieldset>

      <fieldset className="space-y-4" disabled={pending}>
        <legend className="text-lg font-semibold tracking-tight text-foreground">
          Step 2. Choose a location
        </legend>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => {
              setManual(false);
              setError(null);
            }}
            aria-pressed={!manual}
            className={`rounded-full border px-3 py-1.5 text-sm ${
              !manual
                ? "border-primary bg-sage font-medium text-foreground"
                : "border-border text-muted hover:bg-surface-2"
            }`}
          >
            Search by place
          </button>
          <button
            type="button"
            onClick={() => {
              setManual(true);
              setError(null);
            }}
            aria-pressed={manual}
            className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm ${
              manual
                ? "border-primary bg-sage font-medium text-foreground"
                : "border-border text-muted hover:bg-surface-2"
            }`}
          >
            <Crosshair className="size-3.5" aria-hidden="true" />
            Enter coordinates
          </button>
        </div>

        {manual ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label htmlFor="latitude" className="block text-sm font-medium text-foreground">
                Latitude
              </label>
              <input
                id="latitude"
                type="number"
                inputMode="decimal"
                step="any"
                min="-90"
                max="90"
                value={latitude}
                onChange={(event) => setLatitude(event.target.value)}
                placeholder="-1.28333"
                className={selectClasses}
              />
              {latitude.trim() !== "" && !parsedCoordinates.validLat ? (
                <p className="text-xs text-fail">Must be between -90 and 90.</p>
              ) : null}
            </div>
            <div className="space-y-2">
              <label htmlFor="longitude" className="block text-sm font-medium text-foreground">
                Longitude
              </label>
              <input
                id="longitude"
                type="number"
                inputMode="decimal"
                step="any"
                min="-180"
                max="180"
                value={longitude}
                onChange={(event) => setLongitude(event.target.value)}
                placeholder="36.81667"
                className={selectClasses}
              />
              {longitude.trim() !== "" && !parsedCoordinates.validLon ? (
                <p className="text-xs text-fail">Must be between -180 and 180.</p>
              ) : null}
            </div>
          </div>
        ) : (
          <LocationAutocomplete onSelect={setLocation} selected={location} />
        )}
      </fieldset>

      <fieldset className="space-y-4" disabled={pending}>
        <legend className="text-lg font-semibold tracking-tight text-foreground">
          Step 3. Local conditions{" "}
          <span className="text-sm font-normal text-muted">(optional)</span>
        </legend>
        <p className="text-sm text-muted">
          All three are optional. Leaving them blank is honest: those criteria are reported
          as not assessed instead of being guessed.
        </p>

        <div className="grid gap-4 sm:grid-cols-3">
          <div className="space-y-2">
            <label htmlFor="soil" className="block text-sm font-medium text-foreground">
              Soil type
            </label>
            <select
              id="soil"
              value={soil}
              onChange={(event) => setSoil(event.target.value)}
              className={selectClasses}
            >
              <option value="">Not specified</option>
              {SOIL_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label htmlFor="sunlight" className="block text-sm font-medium text-foreground">
              Growing position
            </label>
            <select
              id="sunlight"
              value={sunlight}
              onChange={(event) => setSunlight(event.target.value)}
              className={selectClasses}
            >
              <option value="">Not specified</option>
              {SUNLIGHT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label htmlFor="irrigation" className="block text-sm font-medium text-foreground">
              Irrigation available
            </label>
            <select
              id="irrigation"
              value={irrigation}
              onChange={(event) => setIrrigation(event.target.value)}
              className={selectClasses}
            >
              <option value="">Not specified</option>
              {IRRIGATION_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </fieldset>

      {error ? (
        <p role="alert" className="flex items-start gap-2 rounded-lg border border-fail/35 bg-fail-soft px-4 py-3 text-sm text-fail">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
          {error}
        </p>
      ) : null}

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="submit"
          disabled={pending}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary-hover disabled:opacity-60"
        >
          {pending ? (
            <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
          ) : (
            <Sprout className="size-4" aria-hidden="true" />
          )}
          {pending ? "Opening the assessment…" : "Assess growing suitability"}
        </button>
        <p className="text-xs text-muted">
          The assessment is fetched with real climate records, which can take a few seconds.
        </p>
      </div>
    </form>
  );
}
