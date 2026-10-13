import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet'
import type { GeoJSONFeatureCollection, Municipio, Sismo } from '../types'
import { firstNumber, firstString, num } from '../utils/format'

type Props = { geojson: GeoJSONFeatureCollection | null; municipalities: Municipio[]; earthquakes: Sismo[] }

export default function MapPanel({ geojson, municipalities, earthquakes }: Props) {
  const points: Array<{ lat: number; lng: number; name: string; magnitude?: number; depth?: number; detail: string }> = []
  if (geojson?.features?.length) {
    geojson.features.forEach((feature, i) => {
      const coords = feature.geometry?.coordinates
      if (!coords || coords.length < 2) return
      const p = feature.properties || {}
      points.push({ lng: Number(coords[0]), lat: Number(coords[1]), name: firstString(p, ['municipio', 'nombre', 'name'], `Evento ${i + 1}`), magnitude: firstNumber(p, ['magnitud', 'magnitude']), depth: firstNumber(p, ['profundidad', 'depth']), detail: firstString(p, ['categoria_magnitud', 'nivel', 'categoria'], 'Evento del conjunto de datos') })
    })
  } else {
    const source = municipalities.length ? municipalities : earthquakes
    source.forEach((item, i) => {
      const row = item as Record<string, unknown>
      const lat = firstNumber(row, ['latitud', 'latitude', 'lat'])
      const lng = firstNumber(row, ['longitud', 'longitude', 'lon', 'lng'])
      if (lat === undefined || lng === undefined) return
      points.push({ lat, lng, name: firstString(row, ['municipio', 'nombre'], `Punto ${i + 1}`), magnitude: firstNumber(row, ['magnitud', 'magnitud_maxima']), depth: firstNumber(row, ['profundidad', 'profundidad_media']), detail: firstString(row, ['nivel', 'categoria_magnitud'], 'Dato disponible') })
    })
  }
  return <div className="map-wrap">
    <MapContainer center={[6.85, -73.12]} zoom={8} scrollWheelZoom className="leaflet-map">
      <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {points.map((point, i) => <CircleMarker key={`${point.lat}-${point.lng}-${i}`} center={[point.lat, point.lng]} radius={point.magnitude ? Math.max(5, Math.min(12, point.magnitude * 2)) : 6} pathOptions={{ color: '#38bdf8', fillColor: point.magnitude && point.magnitude >= 4 ? '#fb7185' : '#0ea5e9', fillOpacity: 0.72, weight: 1.5 }}>
        <Popup><div className="map-popup"><b>{point.name}</b><span>{point.detail}</span>{point.magnitude !== undefined && <span>Magnitud: {num(point.magnitude)}</span>}{point.depth !== undefined && <span>Profundidad: {num(point.depth)} km</span>}</div></Popup>
      </CircleMarker>)}
    </MapContainer>
    <div className="map-legend"><span><i className="legend-blue" /> Evento / municipio</span><span><i className="legend-red" /> Magnitud ≥ 4</span></div>
    {!points.length && <div className="map-empty">El mapa se completará cuando la API devuelva coordenadas válidas.</div>}
  </div>
}