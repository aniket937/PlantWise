import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { PlantImage } from "@/components/plant-image";
import { DIFFICULTY_LABEL, LIFECYCLE_LABEL } from "@/lib/format";
import type { PlantSummary } from "@/types/api";

interface PlantCardProps {
  plant: PlantSummary;
  /** Show the image at a larger size on the first card in a grid. */
  preload?: boolean;
}

export function PlantCard({ plant, preload = false }: PlantCardProps) {
  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-xl border border-border bg-surface shadow-[var(--shadow)] transition-colors hover:border-border-strong">
      <Link
        href={`/plants/${plant.slug}`}
        className="flex h-full flex-col"
        aria-label={`View the growing profile for ${plant.common_name}`}
      >
        <PlantImage
          src={plant.image_url}
          alt={plant.common_name}
          sizes="(min-width: 1024px) 320px, (min-width: 640px) 45vw, 90vw"
          preload={preload}
        />

        <div className="flex flex-1 flex-col p-4">
          <h3 className="text-base font-semibold tracking-tight text-foreground">
            {plant.common_name}
          </h3>
          <p className="mt-0.5 text-sm italic text-muted">{plant.scientific_name}</p>

          <p className="mt-3 line-clamp-3 flex-1 text-sm leading-relaxed text-muted">
            {plant.short_description}
          </p>

          <dl className="mt-4 flex flex-wrap gap-1.5 text-xs">
            {plant.lifecycle ? (
              <div className="rounded-full border border-border bg-surface-2 px-2.5 py-1 text-muted">
                <dt className="sr-only">Lifecycle</dt>
                <dd>{LIFECYCLE_LABEL[plant.lifecycle]}</dd>
              </div>
            ) : null}
            {plant.difficulty ? (
              <div className="rounded-full border border-border bg-surface-2 px-2.5 py-1 text-muted">
                <dt className="sr-only">Difficulty</dt>
                <dd>{DIFFICULTY_LABEL[plant.difficulty]}</dd>
              </div>
            ) : null}
          </dl>

          <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-primary">
            Growing profile
            <ArrowRight
              className="size-4 transition-transform group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </span>
        </div>
      </Link>
    </article>
  );
}

/**
 * The same plant as a compact list row, used where a grid would waste space
 * (search results with filter state, related plants).
 */
export function PlantRow({ plant }: { plant: PlantSummary }) {
  return (
    <li className="border-b border-border last:border-b-0">
      <Link
        href={`/plants/${plant.slug}`}
        className="flex items-center gap-4 rounded-lg px-2 py-3 hover:bg-surface-2"
      >
        <div className="size-14 shrink-0">
          <PlantImage
            src={plant.image_url}
            alt={plant.common_name}
            aspectClassName="aspect-square"
            sizes="56px"
          />
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-foreground">
            {plant.common_name}
          </p>
          <p className="truncate text-xs italic text-muted">{plant.scientific_name}</p>
          <p className="mt-1 truncate text-xs text-muted">
            {plant.family ? `${plant.family} · ` : ""}
            {plant.lifecycle ? LIFECYCLE_LABEL[plant.lifecycle] : "Lifecycle not recorded"}
            {plant.tags.length > 0 ? ` · ${plant.tags.slice(0, 2).join(", ")}` : ""}
          </p>
        </div>
        <ArrowRight className="size-4 shrink-0 text-muted" aria-hidden="true" />
      </Link>
    </li>
  );
}
