import { ReactNode } from 'react'

interface CardProps {
  title: string
  children: ReactNode
}

export function Card({ title, children }: CardProps) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-lg">
      <div className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-400">{title}</div>
      {children}
    </div>
  )
}
