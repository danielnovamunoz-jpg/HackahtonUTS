import axios from 'axios'
import type { ApiStatus, GeoJSONFeatureCollection, Municipio, Sismo } from '../types'

const baseURL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: { Accept: 'application/json' },
})

async function getFirst<T>(paths: string[]): Promise<T> {
  let lastError: unknown
  for (const path of paths) {
    try {
      const response = await api.get<T>(path)
      return response.data
    } catch (error) {
      lastError = error
      if (axios.isAxiosError(error) && error.response?.status !== 404 && error.response?.status !== 405) throw error
    }
  }
  throw lastError ?? new Error('No se encontró un endpoint compatible.')
}

export const apiService = {
  health: () => getFirst<ApiStatus>(['/salud', '/health']),
  model: () => getFirst<Record<string, unknown>>(['/modelo']),
  levels: () => getFirst<unknown>(['/niveles']),
  municipalities: () => getFirst<unknown>(['/municipios']),
  geojson: () => getFirst<GeoJSONFeatureCollection>(['/geojson']),
  earthquakes: () => getFirst<unknown>(['/sismos']),
  sources: () => getFirst<unknown>(['/fuentes']),
  summary: () => getFirst<Record<string, unknown>>(['/salidas/resumen']),
  compare: (names: string[]) => api.get('/comparar', { params: { municipios: names.join(',') } }).then(r => r.data),
}

export function arrayFrom<T>(value: unknown): T[] {
  if (Array.isArray(value)) return value as T[]
  if (value && typeof value === 'object') {
    const obj = value as Record<string, unknown>
    for (const key of ['data', 'items', 'resultados', 'municipios', 'sismos', 'niveles', 'features']) {
      if (Array.isArray(obj[key])) return obj[key] as T[]
    }
  }
  return []
}

export function getApiBaseUrl() { return baseURL }