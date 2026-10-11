"use client";

import "leaflet/dist/leaflet.css";

import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";

import type { MapMarker, RegionMapConfig } from "@/types/api";

interface RegionMapInnerProps {
  markers: MapMarker[];
  config: RegionMapConfig;
}

/**
 * Leaflet rendering.
 *
 * Circle markers are used instead of Leaflet's default pin so the map needs no
 * image assets from the CSS, which would otherwise 404 under the bundler.
 */
export default function RegionMapInner({ markers, config }: RegionMapInnerProps) {
  const center: [number, number] = [
    config.default_center[0],
    config.default_center[1],
  ];

  return (
    <MapContainer
      center={center}
      zoom={config.default_zoom}
      scrollWheelZoom={false}
      className="rounded-xl"
    >
      <TileLayer
        url={config.tile_url ?? "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"}
        attribution={`&copy; ${config.attribution ?? "OpenStreetMap contributors"}`}
      />
      {markers.map((marker) => (
        <CircleMarker
          key={marker.slug}
          center={[marker.latitude, marker.longitude]}
          radius={7}
          pathOptions={{
            color: "#244b35",
            fillColor: "#d9a66c",
            fillOpacity: 0.85,
            weight: 2,
          }}
        >
          <Popup>
            <span className="block text-sm font-semibold">{marker.name}</span>
            <span className="block text-xs text-muted">{marker.country}</span>
            <span className="mt-1 block text-xs tabular-nums text-muted">
              {marker.latitude.toFixed(3)}, {marker.longitude.toFixed(3)}
            </span>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
