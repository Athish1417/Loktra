import { useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { Link } from "react-router-dom";
import { priorityColor } from "../lib/constants";

// Marker colors by urgency: Critical(Emergency)=red, High=orange, Medium=blue, Low=green.
const MARKER_COLORS = {
  Emergency: "#E5484D",
  High: "#F5820B",
  Medium: "#3B82F6",
  Low: "#12A150",
};
const markerColor = (u) => MARKER_COLORS[u] || MARKER_COLORS.Medium;

// Free/open tile layers — no API key. Street (CARTO) + satellite (Esri World Imagery).
const LAYERS = {
  map: {
    url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; CARTO',
  },
  satellite: {
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: "Tiles &copy; Esri — Source: Esri, Maxar, Earthstar Geographics",
  },
};

// Dumb map: parent supplies `points` [{position:[lat,lng], ...}] and a center.
export default function ConstituencyMap({ points = [], center, zoom = 13 }) {
  const [layer, setLayer] = useState("map");
  const fallback = center || points[0]?.position || [19.076, 72.8777];
  const tiles = LAYERS[layer];

  return (
    <div className="relative h-full min-h-[320px] w-full overflow-hidden rounded-2xl">
      <div className="absolute right-3 top-3 z-[1000] flex overflow-hidden rounded-lg border border-hairline bg-white shadow-card">
        {["map", "satellite"].map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => setLayer(k)}
            className={`px-3 py-1.5 text-xs font-600 capitalize transition ${
              layer === k ? "bg-ink text-white" : "bg-white text-muted hover:text-body"
            }`}
          >
            {k}
          </button>
        ))}
      </div>

      <MapContainer
        center={fallback}
        zoom={zoom}
        scrollWheelZoom={false}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer key={layer} attribution={tiles.attribution} url={tiles.url} />
        {points.map((p) => {
          const color = markerColor(p.urgency);
          return (
            <CircleMarker
              key={p.id}
              center={p.position}
              radius={p.is_emergency ? 11 : 8}
              pathOptions={{
                color: "#fff",
                weight: 2,
                fillColor: color,
                fillOpacity: 0.9,
              }}
            >
              <Popup>
                <div className="min-w-[180px]">
                  <p className="text-[13px] font-600 text-body">{p.title}</p>
                  <p className="mt-0.5 font-mono text-[11px] text-muted">{p.code}</p>
                  <div className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-[11px]">
                    <span className="font-700" style={{ color: priorityColor(p.score) }}>
                      {Math.round(p.score)}/100
                    </span>
                    <span className="text-muted">·</span>
                    <span style={{ color }}>{p.urgency}</span>
                    {p.category && (
                      <>
                        <span className="text-muted">·</span>
                        <span className="text-body">{p.category}</span>
                      </>
                    )}
                  </div>
                  {p.status && (
                    <p className="mt-1 text-[11px] text-muted">
                      Status: <span className="font-600 text-body">{p.status}</span>
                    </p>
                  )}
                  <Link
                    to={`/app/complaint/${p.id}`}
                    className="mt-1.5 inline-block text-[12px] font-600 text-royal hover:underline"
                  >
                    Open details →
                  </Link>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
