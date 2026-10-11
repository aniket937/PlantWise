"use client";

import { MapPin, Search, X } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";

import type { GeocodedLocation, LocationSearchResponse } from "@/types/api";

interface LocationAutocompleteProps {
  /** Called with the chosen place, or null when the selection is cleared. */
  onSelect: (location: GeocodedLocation | null) => void;
  selected: GeocodedLocation | null;
}

const DEBOUNCE_MS = 350;

/**
 * Debounced place search.
 *
 * Queries are sent to a server-side proxy. A provider outage is surfaced as an
 * inline message and the user is pointed at coordinate entry, so search failing
 * never blocks the task.
 */
export function LocationAutocomplete({ onSelect, selected }: LocationAutocompleteProps) {
  const listId = useId();
  const inputId = useId();
  const [term, setTerm] = useState("");
  const [results, setResults] = useState<GeocodedLocation[]>([]);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState(false);
  const controllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const trimmed = term.trim();
    if (selected && trimmed === selected.label) return;
    // Short terms are cleared in the change handler; nothing to fetch here.
    if (trimmed.length < 2) return;

    const timer = window.setTimeout(async () => {
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;
      setBusy(true);
      try {
        const response = await fetch(
          `/api/locations?q=${encodeURIComponent(trimmed)}`,
          { signal: controller.signal },
        );
        const payload = (await response.json()) as LocationSearchResponse;
        setResults(payload.results);
        setNotice(payload.unavailable_reason);
        setOpen(true);
      } catch (error) {
        if (!(error instanceof DOMException && error.name === "AbortError")) {
          setResults([]);
          setNotice("Place search could not be reached. You can enter coordinates instead.");
        }
      } finally {
        setBusy(false);
      }
    }, DEBOUNCE_MS);

    return () => {
      window.clearTimeout(timer);
    };
  }, [term, selected]);

  useEffect(() => {
    return () => controllerRef.current?.abort();
  }, []);

  function reset() {
    controllerRef.current?.abort();
    controllerRef.current = null;
    setResults([]);
    setOpen(false);
    setNotice(null);
    setBusy(false);
  }

  function choose(location: GeocodedLocation) {
    onSelect(location);
    setTerm(location.label);
    reset();
  }

  function clear() {
    onSelect(null);
    setTerm("");
    reset();
  }

  return (
    <div className="space-y-2">
      <label htmlFor={inputId} className="block text-sm font-medium text-foreground">
        Search for a town or city
      </label>
      <div className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted">
          <Search className="size-4" aria-hidden="true" />
        </span>
        <input
          id={inputId}
          type="text"
          value={term}
          onChange={(event) => {
            const next = event.target.value;
            setTerm(next);
            if (selected) onSelect(null);
            if (next.trim().length < 2) reset();
          }}
          onFocus={() => {
            if (results.length > 0) setOpen(true);
          }}
          role="combobox"
          aria-expanded={open}
          aria-controls={listId}
          aria-autocomplete="list"
          aria-describedby={`${inputId}-help`}
          autoComplete="off"
          placeholder="e.g. Nairobi, Kenya"
          className="w-full rounded-lg border border-border bg-surface py-2.5 pl-9 pr-10 text-sm text-foreground placeholder:text-muted"
        />
        {term ? (
          <button
            type="button"
            onClick={clear}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1.5 text-muted hover:bg-surface-2 hover:text-foreground"
          >
            <X className="size-4" aria-hidden="true" />
            <span className="sr-only">Clear the selected place</span>
          </button>
        ) : null}
      </div>

      <p id={`${inputId}-help`} className="text-xs text-muted">
        {busy
          ? "Searching…"
          : selected
            ? `Selected: ${selected.label}`
            : "Pick a result to use its coordinates, or enter coordinates directly below."}
      </p>

      {notice && !busy ? (
        <p role="status" className="text-xs text-caution">
          {notice}
        </p>
      ) : null}

      {open && results.length > 0 ? (
        <ul
          id={listId}
          role="listbox"
          aria-label="Place search results"
          className="max-h-72 overflow-auto rounded-lg border border-border bg-surface shadow-[var(--shadow)]"
        >
          {results.map((location) => (
            <li key={`${location.latitude},${location.longitude},${location.label}`} role="option" aria-selected={false}>
              <button
                type="button"
                onClick={() => choose(location)}
                className="flex w-full items-start gap-3 border-b border-border px-3 py-2.5 text-left last:border-b-0 hover:bg-surface-2"
              >
                <MapPin className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden="true" />
                <span className="min-w-0">
                  <span className="block truncate text-sm text-foreground">
                    {location.name}
                  </span>
                  <span className="block truncate text-xs text-muted">
                    {[location.admin_area, location.admin_area_2, location.country]
                      .filter(Boolean)
                      .join(", ")}
                  </span>
                  <span className="mt-0.5 block text-xs tabular-nums text-muted">
                    {location.latitude.toFixed(3)}, {location.longitude.toFixed(3)}
                  </span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
