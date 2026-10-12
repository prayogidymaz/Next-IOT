"use client";

import "leaflet/dist/leaflet.css";

import { Circle, MapContainer, Marker, Polygon, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import { Fragment, useEffect } from "react";

import type { FarmMapData } from "@/lib/agriculture/api";

function moistureColor(pct: number | null): string {
  if (pct === null) return "#94A3B8";
  if (pct < 30) return "#EF4444";
  if (pct <= 60) return "#F59E0B";
  return "#10B981";
}

function FitBounds({ bounds }: { bounds: FarmMapData["bounds"] }) {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(
      [
        [bounds.south, bounds.west],
        [bounds.north, bounds.east],
      ],
      { padding: [24, 24] },
    );
  }, [map, bounds]);
  return null;
}

function plotRing(polygon: Record<string, unknown>): [number, number][] {
  const coords = polygon.coordinates;
  if (!Array.isArray(coords) || !Array.isArray(coords[0])) return [];
  const ring = coords[0] as number[][];
  return ring.map((c) => [c[1], c[0]] as [number, number]);
}

export function FarmMap({ data, farmId }: { data: FarmMapData; farmId: string }) {
  const center: [number, number] = [
    (data.bounds.north + data.bounds.south) / 2,
    (data.bounds.east + data.bounds.west) / 2,
  ];
  return (
    <MapContainer center={center} zoom={12} minZoom={10} maxZoom={19} className="h-[420px] w-full rounded-xl">
      <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <FitBounds bounds={data.bounds} />
      {data.plots.map((plot) => {
        const ring = plotRing(plot.polygon);
        if (ring.length < 3) return null;
        return (
          <Polygon
            key={plot.id}
            positions={ring}
            pathOptions={{
              color: moistureColor(plot.moisture_pct),
              fillColor: moistureColor(plot.moisture_pct),
              fillOpacity: 0.4,
              weight: 2,
            }}
          />
        );
      })}
      {data.sensors.map((s) => {
        if (s.lat === null || s.lng === null) return null;
        return (
          <Marker key={s.id} position={[s.lat, s.lng]}>
            <Popup>
              <p className="font-medium">{s.name}</p>
              <p className="text-xs">{s.sensor_type}</p>
              <a className="text-emerald-700 text-xs" href={`/agriculture/farms/${farmId}/sensors/${s.id}`}>
                View detail
              </a>
            </Popup>
          </Marker>
        );
      })}
      {data.gateways.map((g) => {
        if (g.lat === null || g.lng === null) return null;
        return (
          <Fragment key={g.id}>
            <Marker position={[g.lat, g.lng]} />
            <Circle center={[g.lat, g.lng]} radius={5000} pathOptions={{ color: "#38BDF8", fillOpacity: 0.08 }} />
          </Fragment>
        );
      })}
      {data.valves.map((v) => {
        if (v.lat === null || v.lng === null) return null;
        const icon = L.divIcon({
          className: "",
          html: `<div style="width:12px;height:12px;border-radius:50%;background:${v.current_state === "open" ? "#10B981" : "#9CA3AF"}"></div>`,
        });
        return <Marker key={v.id} position={[v.lat, v.lng]} icon={icon} />;
      })}
    </MapContainer>
  );
}
