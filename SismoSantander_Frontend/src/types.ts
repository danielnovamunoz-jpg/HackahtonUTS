export type Municipio = {
  municipio?: string
  nombre?: string
  codigo?: string | number
  departamento?: string
  latitud?: number
  longitud?: number
  magnitud_media?: number
  magnitud_promedio?: number
  magnitud_maxima?: number
  profundidad_media?: number
  profundidad_promedio?: number
  cantidad_sismos?: number
  total_sismos?: number
  nivel?: string
  cluster?: number | string
  [key: string]: unknown
}

export type Sismo = {
  municipio?: string
  departamento?: string
  año?: number
  anio?: number
  mes?: number
  dia?: number
  latitud?: number
  longitud?: number
  profundidad?: number
  magnitud?: number
  categoria_magnitud?: string
  categoria_profundidad?: string
  [key: string]: unknown
}

export type GeoJSONFeatureCollection = {
  type: 'FeatureCollection'
  features: Array<{
    type: 'Feature'
    geometry: { type: 'Point'; coordinates: [number, number] } | null
    properties?: Record<string, unknown>
  }>
}

export type ApiStatus = {
  estado?: string
  status?: string
  listo?: boolean
  mensaje?: string
  error?: string
  [key: string]: unknown
}