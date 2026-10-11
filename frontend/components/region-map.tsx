"use client";

import dynamic from "next/dynamic";
import { Layers } from "lucide-react";

import type { MapMarker, RegionMapConfig } from "@/types/api";

const RegionMapInner = dynamic(() => import("@/components/region-map-inner"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center rounded-xl border border-border bg-surface-2">
      <p className="text-sm text-muted">Loading the map…</p>
    </div>
  ),
});

interface RegionMapProps {
  markers: MapMarker[];
  config: RegionMapConfig;
}

/**
 * Map panel. The map is explicitly a *secondary* view: the region list rendered
 * alongside it carries the same information, so nothing is map-only.
 */
export function RegionMap({ markers, config }: RegionMapProps) {
  if (!config.available || markers.length === 0) {
    return (
      <div className="flex h-[360px] w-full flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-border-strong bg-surface-2 p-6 text-center">
        <Layers className="size-5 text-muted" aria-hidden="true" />
        <p className="text-sm font-medium text-foreground">Map not available</p>
        <p className="max-w-sm text-xs leading-relaxed text-muted">{config.detail}</p>
      </div>
    );
  }

  return (
    <div className="h-[360px] w-full overflow-hidden rounded-xl border border-border sm:h-[440px]">
      <RegionMapInner markers={markers} config={config} />
    </div>
  );
}
