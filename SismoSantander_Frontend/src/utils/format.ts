export function num(value: unknown, digits = 1): string {
  const parsed = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(parsed) ? parsed.toLocaleString('es-CO', { maximumFractionDigits: digits }) : '—'
}

export function firstNumber(obj: Record<string, unknown>, keys: string[]): number | undefined {
  for (const key of keys) {
    const value = Number(obj[key])
    if (obj[key] !== undefined && obj[key] !== null && obj[key] !== '' && Number.isFinite(value)) return value
  }
  return undefined
}

export function firstString(obj: Record<string, unknown>, keys: string[], fallback = 'Sin dato'): string {
  for (const key of keys) {
    const value = obj[key]
    if (typeof value === 'string' && value.trim()) return value
    if (typeof value === 'number') return String(value)
  }
  return fallback
}

export function prettyKey(key: string): string {
  return key.replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase())
}

export function safeArray(value: unknown): unknown[] {
  if (Array.isArray(value)) return value
  if (value && typeof value === 'object') {
    const obj = value as Record<string, unknown>
    for (const key of ['data', 'items', 'resultados', 'municipios', 'sismos', 'niveles', 'features']) {
      if (Array.isArray(obj[key])) return obj[key] as unknown[]
    }
  }
  return []
}