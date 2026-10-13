import { useCallback, useEffect, useMemo, useState } from 'react'

import { Activity, AlertCircle, ArrowUpRight, BarChart3, CheckCircle2, Clock3, Compass, Database, Download, Layers3, Menu, RefreshCw, Search, ShieldAlert, Signal, Wifi, WifiOff, Zap } from 'lucide-react'

import { CartesianGrid, Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import Sidebar from './components/Sidebar'

import StatCard from './components/StatCard'

import Panel from './components/Panel'

import MapPanel from './components/MapPanel'

import { apiService, arrayFrom, getApiBaseUrl } from './services/api'

import type { ApiStatus, GeoJSONFeatureCollection, Municipio, Sismo } from './types'

import { firstNumber, firstString, num, prettyKey, safeArray } from './utils/format'

type LoadState = 'loading' | 'online' | 'offline'

const asRecord = (v: unknown): Record<string, unknown> => v && typeof v === 'object' ? v as Record<string, unknown> : {}

export default function App() {

  const [page, setPage] = useState('dashboard')

  const [mobileOpen, setMobileOpen] = useState(false)

  const [loadState, setLoadState] = useState<LoadState>('loading')

  const [health, setHealth] = useState<ApiStatus | null>(null)

  const [municipalities, setMunicipalities] = useState<Municipio[]>([])

  const [earthquakes, setEarthquakes] = useState<Sismo[]>([])

  const [geojson, setGeojson] = useState<GeoJSONFeatureCollection | null>(null)

  const [model, setModel] = useState<Record<string, unknown>>({})

  const [levels, setLevels] = useState<unknown>([])

  const [sources, setSources] = useState<unknown>([])

  const [summary, setSummary] = useState<Record<string, unknown>>({})

  const [error, setError] = useState('')

  const [search, setSearch] = useState('')

  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const loadData = useCallback(async () => {

    setLoadState('loading'); setError('')

    try {

      const results = await Promise.allSettled([

        apiService.health(), apiService.municipalities(), apiService.earthquakes(),

        apiService.geojson(), apiService.model(), apiService.levels(),

        apiService.sources(), apiService.summary(),

      ])

      const [h, m, s, g, mo, l, so, su] = results

      if (h.status === 'rejected' && m.status === 'rejected' && s.status === 'rejected') {

        throw new Error('No se pudo conectar con la API. Verifica que FastAPI esté ejecutándose y que VITE_API_URL sea correcto.')

      }

      if (h.status === 'fulfilled') setHealth(h.value)

      if (m.status === 'fulfilled') setMunicipalities(arrayFrom<Municipio>(m.value))

      if (s.status === 'fulfilled') setEarthquakes(arrayFrom<Sismo>(s.value))

      if (g.status === 'fulfilled' && g.value?.type === 'FeatureCollection') setGeojson(g.value)

      if (mo.status === 'fulfilled') setModel(mo.value)

      if (l.status === 'fulfilled') setLevels(l.value)

      if (so.status === 'fulfilled') setSources(so.value)

      if (su.status === 'fulfilled') setSummary(su.value)

      setLoadState('online'); setLastUpdated(new Date())

      const failed = results.filter(r => r.status === 'rejected').length

      if (failed > 0) setError(`${failed} de 8 endpoints no respondieron; se mostrarán los datos disponibles.`)

    } catch (e) {

      setLoadState('offline')

      setError(e instanceof Error ? e.message : 'Error al conectar con la API.')

    }

  }, [])

  useEffect(() => { void loadData() }, [loadData])

  const filteredMunicipalities = useMemo(() => municipalities.filter(item => {

    const row = item as Record<string, unknown>

    const name = firstString(row, ['municipio', 'nombre'], '')

    return name.toLowerCase().includes(search.toLowerCase())

  }), [municipalities, search])

  const summaryObj = asRecord(summary)

  const modelObj = asRecord(model)

  const totalEvents = firstNumber(summaryObj, ['total_sismos', 'cantidad_sismos', 'total_eventos', 'n_sismos']) ?? earthquakes.length

  const totalMunicipalities = firstNumber(summaryObj, ['total_municipios', 'municipios_analizados', 'n_municipios']) ?? municipalities.length

  const maxMagnitude = firstNumber(summaryObj, ['magnitud_maxima', 'max_magnitud', 'magnitud_max']) ?? Math.max(0, ...earthquakes.map(s => Number(s.magnitud) || 0))

  const avgDepth = firstNumber(summaryObj, ['profundidad_media', 'profundidad_promedio', 'media_profundidad']) ?? (earthquakes.length ? earthquakes.reduce((sum, s) => sum + (Number(s.profundidad) || 0), 0) / earthquakes.length : undefined)

  const chartData = useMemo(() => {

    const counts = new Map<string, number>()

    earthquakes.forEach(item => {

      const row = item as Record<string, unknown>

      const category = firstString(row, ['categoria_magnitud'], Number.isFinite(Number(row.magnitud)) ? `M ${Math.floor(Number(row.magnitud))}` : 'Sin categoría')

      counts.set(category, (counts.get(category) || 0) + 1)

    })

    if (counts.size) return Array.from(counts.entries()).map(([name, cantidad]) => ({ name, cantidad })).slice(0, 8)

    return municipalities.slice(0, 8).map(m => {

      const row = m as Record<string, unknown>

      return { name: firstString(row, ['municipio', 'nombre'], 'Municipio'), cantidad: firstNumber(row, ['cantidad_sismos', 'total_sismos', 'n_sismos']) ?? 0 }

    }).filter(x => x.cantidad > 0)

  }, [earthquakes, municipalities])

  const modelStatus = firstString(modelObj, ['estado', 'status', 'algoritmo', 'modelo'], 'Información no disponible')

  const pageTitle: Record<string, string> = { dashboard: 'Resumen general', mapa: 'Mapa sísmico', municipios: 'Explorador de municipios', analisis: 'Análisis del modelo', configuracion: 'Conexión API' }

  const exportMunicipalities = () => {

    const rows = filteredMunicipalities.map(m => Object.entries(m).map(([k, v]) => `${String(v ?? '').replaceAll('"', '""')}`).join(','))

    const headers = filteredMunicipalities.length ? Object.keys(filteredMunicipalities[0]) : []

    const csv = [headers.join(','), ...rows].join('\n')

    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }))

    const a = document.createElement('a'); a.href = url; a.download = 'sismosantander-municipios.csv'; a.click(); URL.revokeObjectURL(url)

  }

  return <div className="app-shell">

    <Sidebar page={page} setPage={setPage} mobileOpen={mobileOpen} closeMobile={() => setMobileOpen(false)} />

    <main className="main-area">

      <header className="topbar">

        <button className="mobile-menu icon-button" aria-label="Abrir menú" onClick={() => setMobileOpen(true)}><Menu size={21} /></button>

        <div className="breadcrumb"><span>Plataforma</span><b>/</b><strong>{pageTitle[page] || 'Resumen general'}</strong></div>

        <div className="topbar-right">

          <div className={`connection-pill ${loadState}`}><span className="status-dot" />{loadState === 'online' ? 'API conectada' : loadState === 'loading' ? 'Conectando…' : 'API desconectada'}</div>

          <button className="icon-button" title="Actualizar datos" onClick={() => void loadData()}><RefreshCw size={17} className={loadState === 'loading' ? 'spin' : ''} /></button>

          <div className="avatar">SS</div>

        </div>

      </header>

      <div className="page-content">

        <div className="page-title-row">

          <div><div className="eyebrow"><span className="eyebrow-line" /> OBSERVATORIO SÍSMICO · SANTANDER</div><h1>{pageTitle[page] || 'Resumen general'}</h1><p className="page-subtitle">Visualización y análisis de eventos sísmicos a partir del conjunto de datos del proyecto.</p></div>

          <button className="button-secondary" onClick={() => void loadData()}><RefreshCw size={15} /> Actualizar datos</button>

        </div>

        {error && <div className={`notice ${loadState === 'offline' ? 'notice-error' : 'notice-warn'}`}><AlertCircle size={18} /><div><b>{loadState === 'offline' ? 'No hay conexión con la API' : 'Conexión parcial'}</b><p>{error}</p>{loadState === 'offline' && <button onClick={() => setPage('configuracion')}>Revisar configuración</button>}</div></div>}

        {page === 'dashboard' && <>

          <div className="stats-grid">

            <StatCard label="Eventos sísmicos" value={num(totalEvents, 0)} detail="Registros disponibles en la API" icon={Activity} tone="blue" />

            <StatCard label="Municipios analizados" value={num(totalMunicipalities, 0)} detail="Municipios en el conjunto de datos" icon={Compass} tone="cyan" />

            <StatCard label="Magnitud máxima" value={maxMagnitude ? num(maxMagnitude, 2) : '—'} detail="Mayor magnitud disponible" icon={Zap} tone="amber" />

            <StatCard label="Profundidad media" value={avgDepth !== undefined ? `${num(avgDepth)} km` : '—'} detail="Promedio de profundidad registrada" icon={Layers3} tone="violet" />

          </div>

          <div className="dashboard-grid">

            <Panel title="Distribución geográfica" subtitle="Ubicación de eventos y municipios" className="map-panel" action={<button className="text-action" onClick={() => setPage('mapa')}>Ver mapa completo <ArrowUpRight size={14} /></button>}>

              <MapPanel geojson={geojson} municipalities={municipalities} earthquakes={earthquakes} />

            </Panel>

            <Panel title="Distribución por categoría" subtitle="Frecuencia de registros por magnitud">

              {chartData.length ? <div className="chart-area"><ResponsiveContainer width="100%" height="100%"><BarChart data={chartData} margin={{ top: 12, right: 4, left: -22, bottom: 6 }}><CartesianGrid stroke="#1b3043" strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" tick={{ fill: '#8296a9', fontSize: 10 }} axisLine={false} tickLine={false} /><YAxis tick={{ fill: '#8296a9', fontSize: 10 }} axisLine={false} tickLine={false} /><Tooltip contentStyle={{ background: '#0d1b2a', border: '1px solid #23394d', borderRadius: 10, color: '#e5eef6' }} cursor={{ fill: '#14283a' }} /><Bar dataKey="cantidad" name="Registros" radius={[5, 5, 0, 0]}>{chartData.map((_, i) => <Cell key={i} fill={i % 2 ? '#0ea5e9' : '#38bdf8'} />)}</Bar></BarChart></ResponsiveContainer></div> : <div className="empty-state"><BarChart3 size={25} /><b>Sin datos para graficar</b><span>La API no ha devuelto eventos con magnitud o categoría.</span></div>}

            </Panel>

          </div>

          <div className="bottom-grid">

            <Panel title="Municipios destacados" subtitle="Primeros resultados reportados por el modelo" action={<button className="text-action" onClick={() => setPage('municipios')}>Ver todos <ArrowUpRight size={14} /></button>}>

              <MunicipalityTable rows={municipalities.slice(0, 5)} />

            </Panel>

            <Panel title="Estado del análisis" subtitle="Información de los modelos disponibles">

              <div className="model-status"><div className={`model-status-icon ${loadState === 'online' ? 'good' : 'bad'}`}>{loadState === 'online' ? <CheckCircle2 size={19} /> : <ShieldAlert size={19} />}</div><div><b>{loadState === 'online' ? 'API accesible' : 'Verifica el servidor'}</b><span>{modelStatus}</span></div><span className={`mini-tag ${loadState === 'online' ? 'tag-good' : 'tag-bad'}`}>{loadState === 'online' ? 'DISPONIBLE' : 'PENDIENTE'}</span></div>

              <div className="model-metrics"><div><span>Modelo / método</span><b>{firstString(modelObj, ['algoritmo', 'modelo', 'metodo'], 'Consultar API')}</b></div><div><span>Última actualización</span><b>{lastUpdated ? lastUpdated.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }) : '—'}</b></div></div>

              <p className="disclaimer">Los niveles y agrupaciones son resultados analíticos del conjunto de datos; no equivalen a una alerta oficial ni a una predicción de sismos.</p>

            </Panel>

          </div>

        </>}

        {page === 'mapa' && <div className="single-panel"><Panel title="Mapa de eventos" subtitle="Selecciona un punto del mapa para consultar sus atributos."><MapPanel geojson={geojson} municipalities={municipalities} earthquakes={earthquakes} /></Panel><div className="map-footnote">El mapa utiliza OpenStreetMap como cartografía base. La disponibilidad de puntos depende de las coordenadas devueltas por la API.</div></div>}

        {page === 'municipios' && <Panel title="Municipios de Santander" subtitle={`${filteredMunicipalities.length} resultados disponibles`} action={<button className="button-secondary" onClick={exportMunicipalities}><Download size={15} /> Exportar CSV</button>}>

          <div className="table-toolbar"><div className="search-box"><Search size={16} /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Buscar municipio..." /></div><span className="table-count">{filteredMunicipalities.length} municipios</span></div>

          <MunicipalityTable rows={filteredMunicipalities} expanded />

          {!filteredMunicipalities.length && <div className="empty-state"><Database size={25} /><b>No hay municipios para mostrar</b><span>Comprueba que la API tenga datos cargados.</span></div>}

        </Panel>}

        {page === 'analisis' && <div className="analysis-grid">

          <Panel title="Información del modelo" subtitle="Metadatos disponibles en el endpoint /modelo"><KeyValueList data={model} /></Panel>

          <Panel title="Niveles calculados" subtitle="Salida reportada por el endpoint /niveles"><GenericData data={levels} /></Panel>

          <Panel title="Fuentes y datos" subtitle="Contenido reportado por el endpoint /fuentes"><GenericData data={sources} /></Panel>

          <Panel title="Resumen de ejecución" subtitle="Indicadores reportados por la API"><KeyValueList data={summary} /></Panel>

        </div>}

        {page === 'configuracion' && <div className="settings-grid">

          <Panel title="Conexión con FastAPI" subtitle="Dirección base que utiliza el frontend">

            <div className="api-address"><div className={`api-address-icon ${loadState}`}><Signal size={20} /></div><div><span>URL de la API</span><strong>{getApiBaseUrl()}</strong></div><span className={`mini-tag ${loadState === 'online' ? 'tag-good' : loadState === 'offline' ? 'tag-bad' : ''}`}>{loadState === 'online' ? 'CONECTADA' : loadState === 'offline' ? 'SIN CONEXIÓN' : 'CONECTANDO'}</span></div>

            <div className="settings-steps"><b>Cómo cambiar la URL</b><ol><li>Crea un archivo <code>.env</code> en la raíz del frontend.</li><li>Agrega <code>VITE_API_URL=http\://127.0.0.1:8000</code>.</li><li>Reinicia Vite con <code>npm run dev</code>.</li></ol><p>Si abres el frontend desde otro equipo, cambia la dirección por la IP o el dominio del servidor donde corre FastAPI.</p></div>

            <div className="settings-actions"><button className="button-primary" onClick={() => void loadData()}><RefreshCw size={15} /> Probar conexión</button><button className="button-secondary" onClick={() => window.open(`${getApiBaseUrl()}/docs`, '_blank', 'noopener,noreferrer')}>Abrir Swagger <ArrowUpRight size={14} /></button></div>

          </Panel>

          <Panel title="Estado del servicio" subtitle="Respuesta del endpoint /salud">

            {health ? <KeyValueList data={health as Record<string, unknown>} /> : <div className="empty-state"><WifiOff size={24} /><b>Sin respuesta de salud</b><span>La API no devolvió información del endpoint /salud.</span></div>}

            {loadState === 'online' && <div className="success-line"><CheckCircle2 size={16} /> El frontend logró consultar al menos uno de los endpoints principales.</div>}

            <div className="settings-link"><Wifi size={16} /><a href={`${getApiBaseUrl()}/docs`} target="_blank" rel="noreferrer">Abrir documentación interactiva</a></div>

          </Panel>

        </div>}

        <footer className="page-footer"><span>© 2026 SismoSantander · Proyecto académico</span><span><Clock3 size={13} />{lastUpdated ? `Actualizado ${lastUpdated.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}` : 'Esperando datos'}</span></footer>

      </div>

    </main>

  </div>

}

function MunicipalityTable({ rows, expanded = false }: { rows: Municipio[]; expanded?: boolean }) {

  if (!rows.length) return <div className="empty-state compact"><Database size={23} /><b>No hay registros disponibles</b><span>Verifica que la API esté cargando el CSV.</span></div>

  return <div className="table-scroll"><table className="data-table"><thead><tr><th>Municipio</th><th>Magnitud máx.</th><th>Profundidad</th><th>Nivel / grupo</th>{expanded && <th>Departamento</th>}</tr></thead><tbody>{rows.map((item, i) => {

    const row = item as Record<string, unknown>

    const name = firstString(row, ['municipio', 'nombre'], `Registro ${i + 1}`)

    const mag = firstNumber(row, ['magnitud_maxima', 'magnitud_max', 'magnitud_media', 'magnitud_promedio'])

    const depth = firstNumber(row, ['profundidad_media', 'profundidad_promedio', 'profundidad'])

    const level = firstString(row, ['nivel', 'categoria', 'cluster', 'grupo'], 'Sin clasificar')

    return <tr key={`${name}-${i}`}><td><div className="municipality-name"><span className="municipality-avatar">{name.slice(0, 1).toUpperCase()}</span><b>{name}</b></div></td><td>{mag !== undefined ? <span className="magnitude-value">{num(mag, 2)}</span> : '—'}</td><td>{depth !== undefined ? `${num(depth)} km` : '—'}</td><td><span className="level-chip">{level}</span></td>{expanded && <td>{firstString(row, ['departamento'], 'Santander')}</td>}</tr>

  })}</tbody></table></div>

}

function formatScalar(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—'
  if (typeof value === 'boolean') return value ? 'Sí' : 'No'
  if (typeof value === 'number') return Number.isInteger(value) ? value.toLocaleString('es-CO') : value.toLocaleString('es-CO', { maximumFractionDigits: 4 })
  if (typeof value === 'string') return value
  return String(value)
}

function KeyValueList({ data }: { data: unknown }) {
  const record = asRecord(data)
  const entries = Object.entries(record)
  if (!entries.length) return <div className="empty-state compact"><Database size={23} /><b>Sin metadatos</b><span>Este endpoint no ha devuelto información.</span></div>

  return <div className="key-value-list">
    {entries.map(([key, value]) => {
      const isArray = Array.isArray(value)
      const isObject = value !== null && typeof value === 'object' && !isArray
      return <div className={`key-value-row ${isArray || isObject ? 'key-value-complex' : ''}`} key={key}>
        <span className="key-value-label">{prettyKey(key)}</span>
        {isArray && value.every(item => typeof item === 'string' || typeof item === 'number') ? (
          <div className="value-chips">{value.map((item, index) => <span className="value-chip" key={`${String(item)}-${index}`}>{String(item)}</span>)}</div>
        ) : isArray ? (
          <div className="nested-value"><GenericData data={value} /></div>
        ) : isObject ? (
          <div className="nested-value"><KeyValueList data={value} /></div>
        ) : <strong className="key-value-value">{formatScalar(value)}</strong>}
      </div>
    })}
  </div>
}

function GenericData({ data }: { data: unknown }) {
  const arr = safeArray(data)
  if (arr.length) {
    const first = arr[0]
    if (first && typeof first === 'object' && !Array.isArray(first)) {
      const records = arr.filter((item): item is Record<string, unknown> => !!item && typeof item === 'object' && !Array.isArray(item))
      const looksLikeLevel = records.some(row => 'lista_municipios' in row && 'nivel' in row)
      const looksLikeSource = records.some(row => 'fuente_id' in row && ('codigo' in row || 'cantidad_sismos' in row))

      if (looksLikeLevel) {
        return <div className="level-list">
          {records.map((row, index) => {
            const color = typeof row.color === 'string' ? row.color : '#38bdf8'
            const names = Array.isArray(row.lista_municipios) ? row.lista_municipios : []
            return <article className="level-card" key={`${String(row.nivel ?? 'nivel')}-${index}`}>
              <div className="level-card-heading">
                <span className="level-number">{String(index + 1).padStart(2, '0')}</span>
                <span className="level-color-dot" style={{ backgroundColor: color }} />
                <strong>{formatScalar(row.nivel)}</strong>
                <span className="level-count">{formatScalar(row.municipios)} municipios</span>
              </div>
              <div className="level-card-metrics"><span>Índice medio <b>{formatScalar(row.indice_medio)}</b></span><span>Municipios <b>{names.length}</b></span></div>
              <details className="municipality-details">
                <summary>Ver municipios ({names.length})</summary>
                <div className="value-chips">{names.map((name, i) => <span className="value-chip" key={`${String(name)}-${i}`}>{String(name)}</span>)}</div>
              </details>
            </article>
          })}
        </div>
      }

      if (looksLikeSource) {
        return <div className="source-list">
          {records.map((row, index) => <article className="source-card" key={`${String(row.fuente_id ?? index)}`}>
            <div className="source-card-heading"><strong>{formatScalar(row.codigo ?? `Fuente ${index + 1}`)}</strong><span>{formatScalar(row.tipo)}</span></div>
            <div className="source-metrics">
              <div><span>Eventos</span><b>{formatScalar(row.cantidad_sismos)}</b></div>
              <div><span>Magnitud máxima</span><b>{formatScalar(row.magnitud_maxima)}</b></div>
              <div><span>Profundidad mediana</span><b>{row.profundidad_mediana_km !== undefined ? `${formatScalar(row.profundidad_mediana_km)} km` : '—'}</b></div>
              <div><span>Confianza media</span><b>{row.confianza_media !== undefined ? `${(Number(row.confianza_media) * 100).toLocaleString('es-CO', { maximumFractionDigits: 1 })}%` : '—'}</b></div>
            </div>
            <details className="municipality-details"><summary>Detalles de ubicación</summary><div className="source-location">Latitud: {formatScalar(row.lat)} · Longitud: {formatScalar(row.lon)}</div></details>
          </article>)}
        </div>
      }
      return <div className="generic-record-list">
        {records.map((row, index) => <article className="generic-record" key={index}><span className="generic-index">{String(index + 1).padStart(2, '0')}</span><KeyValueList data={row} /></article>)}
      </div>
    }
    return <div className="value-chips">{arr.map((item, index) => <span className="value-chip" key={`${String(item)}-${index}`}>{formatScalar(item)}</span>)}</div>
  }
  if (data && typeof data === 'object') return <KeyValueList data={data} />
  return <div className="empty-state compact"><Database size={23} /><b>Sin resultados</b><span>El endpoint no ha devuelto datos.</span></div>
}
