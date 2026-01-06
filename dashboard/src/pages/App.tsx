import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { Card } from '../components/Card'

interface SignalPayload {
  channel: string
  payload: Record<string, unknown>
}

const API_BASE = 'http://localhost:8000'

function LiveSignals() {
  const [signals, setSignals] = useState<SignalPayload[]>([])
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/stream')
    ws.onmessage = (evt) => {
      const data = JSON.parse(evt.data)
      setSignals((prev) => [data, ...prev].slice(0, 20))
    }
    return () => ws.close()
  }, [])
  return (
    <div className="space-y-3">
      {signals.map((s, idx) => (
        <div key={idx} className="rounded-lg border border-slate-800 bg-slate-800/50 p-3">
          <div className="text-xs uppercase text-slate-400">{s.channel}</div>
          <pre className="whitespace-pre-wrap text-xs text-slate-200">{JSON.stringify(s.payload, null, 2)}</pre>
        </div>
      ))}
    </div>
  )
}

function ConfigForm() {
  const [assets, setAssets] = useState<string[]>(['BTCUSDT', 'ETHUSDT'])
  const [mode, setMode] = useState('paper')

  const payload = useMemo(
    () => ({
      assets: assets.map((symbol) => ({ symbol, enabled: true, timeframes: ['1m', '5m'], strategies: {} })),
      risk: { risk_per_trade: 1 },
      execution: { mode },
    }),
    [assets, mode],
  )

  const handleSubmit = async () => {
    await axios.put(`${API_BASE}/config`, payload)
  }

  return (
    <div className="space-y-3">
      <div>
        <label className="text-sm text-slate-300">Modo</label>
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
          className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 p-2 text-slate-100"
        >
          <option value="paper">Paper</option>
          <option value="testnet">Testnet</option>
        </select>
      </div>
      <div>
        <label className="text-sm text-slate-300">Ativos</label>
        <input
          value={assets.join(',')}
          onChange={(e) => setAssets(e.target.value.split(',').map((s) => s.trim()))}
          className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-800 p-2 text-slate-100"
        />
      </div>
      <button
        onClick={handleSubmit}
        className="w-full rounded-lg bg-emerald-500 p-2 font-semibold text-emerald-900 shadow"
      >
        Salvar configuração
      </button>
    </div>
  )
}

function Performance() {
  const [metrics, setMetrics] = useState<any[]>([])
  useEffect(() => {
    axios.get(`${API_BASE}/performance`).then((res) => setMetrics(res.data))
  }, [])
  return (
    <table className="w-full text-sm text-slate-200">
      <thead>
        <tr className="text-left text-slate-400">
          <th>Ativo</th>
          <th>TF</th>
          <th>Sharpe</th>
          <th>Winrate</th>
          <th>Drawdown</th>
        </tr>
      </thead>
      <tbody>
        {metrics.map((m, idx) => (
          <tr key={idx} className="border-b border-slate-800">
            <td>{m.symbol}</td>
            <td>{m.timeframe}</td>
            <td>{m.sharpe}</td>
            <td>{m.winrate}</td>
            <td>{m.max_drawdown}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950">
      <header className="border-b border-slate-800 bg-slate-900/70 p-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white">Agente IA Dashboard</h1>
            <p className="text-sm text-slate-400">Monitoramento, configuração e métricas em tempo real</p>
          </div>
          <div className="rounded-full bg-emerald-500 px-3 py-1 text-sm font-semibold text-emerald-900">Paper</div>
        </div>
      </header>
      <main className="mx-auto grid max-w-6xl gap-6 p-6 md:grid-cols-3">
        <Card title="Configuração">
          <ConfigForm />
        </Card>
        <Card title="Sinais em tempo real">
          <LiveSignals />
        </Card>
        <Card title="Performance">
          <Performance />
        </Card>
      </main>
    </div>
  )
}
