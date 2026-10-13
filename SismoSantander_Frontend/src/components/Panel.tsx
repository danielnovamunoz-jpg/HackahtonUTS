import type { ReactNode } from 'react'
type Props = { title: string; subtitle?: string; action?: ReactNode; children: ReactNode; className?: string }
export default function Panel({ title, subtitle, action, children, className = '' }: Props) {
  return <section className={`panel ${className}`}><div className="panel-heading"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>{action}</div>{children}</section>
}