"use client";

import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

type Marker = { id: string; name: string; lat: number; lng: number };

export default function SiteMapInner({ markers }: { markers: Marker[] }) {
  const center = markers[0];
  return (
    <MapContainer center={[center.lat, center.lng]} zoom={6} className="h-full w-full">
      <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {markers.map((m) => (
        <Marker key={m.id} position={[m.lat, m.lng]}>
          <Popup>{m.name}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
