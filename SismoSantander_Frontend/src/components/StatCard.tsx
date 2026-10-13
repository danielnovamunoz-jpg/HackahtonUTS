import type { LucideIcon } from 'lucide-react'

type Props = { label: string; value: string; detail: string; icon: LucideIcon; tone?: 'blue' | 'cyan' | 'violet' | 'amber' }

export default function StatCard({ label, value, detail, icon: Icon, tone = 'blue' }: Props) {
  return <article className="stat-card">
    <div className={`stat-icon ${tone}`}><Icon size={19} /></div>
    <div className="stat-copy"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>
  </article>
}