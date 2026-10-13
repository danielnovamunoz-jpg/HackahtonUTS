import { Activity, BarChart3, CircleHelp, Database, LayoutDashboard, Map, RadioTower, Settings2 } from 'lucide-react'

type Props = { page: string; setPage: (page: string) => void; mobileOpen: boolean; closeMobile: () => void }

const nav = [
  { id: 'dashboard', label: 'Resumen general', icon: LayoutDashboard },
  { id: 'mapa', label: 'Mapa sísmico', icon: Map },
  { id: 'municipios', label: 'Municipios', icon: Database },
  { id: 'analisis', label: 'Análisis del modelo', icon: BarChart3 },
]

export default function Sidebar({ page, setPage, mobileOpen, closeMobile }: Props) {
  return <>
    {mobileOpen && <button aria-label="Cerrar menú" className="mobile-scrim" onClick={closeMobile} />}
    <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
      <div className="brand">
        <div className="brand-mark"><Activity size={23} strokeWidth={2.4} /></div>
        <div><strong>Sismo<span>Santander</span></strong><small>PLATAFORMA DE ANÁLISIS</small></div>
      </div>
      <div className="side-label">ESPACIO DE TRABAJO</div>
      <nav className="nav-list">
        {nav.map(item => {
          const Icon = item.icon
          return <button key={item.id} className={`nav-item ${page === item.id ? 'active' : ''}`} onClick={() => { setPage(item.id); closeMobile() }}>
            <Icon size={18} /><span>{item.label}</span>{page === item.id && <span className="active-dot" />}
          </button>
        })}
      </nav>
      <div className="sidebar-bottom">
        <div className="data-note"><div className="data-note-icon"><RadioTower size={17} /></div><div><b>Datos locales</b><p>Resultados calculados desde el CSV del proyecto.</p></div></div>
        <button className={`nav-item ${page === 'configuracion' ? 'active' : ''}`} onClick={() => { setPage('configuracion'); closeMobile() }}><Settings2 size={18} /><span>Conexión API</span></button>
        <button className="nav-item" onClick={() => window.open('http://127.0.0.1:8000/docs', '_blank', 'noopener,noreferrer')}><CircleHelp size={18} /><span>Documentación API</span></button>
      </div>
      <div className="sidebar-footer"><span className="status-dot" />SismoSantander <span className="version">v1.0</span></div>
    </aside>
  </>
}