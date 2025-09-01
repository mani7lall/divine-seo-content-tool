import { useState } from 'react'

const API = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function Research() {
  const [seeds, setSeeds] = useState('best hiking backpacks')
  const [loading, setLoading] = useState(false)
  const [resp, setResp] = useState<any>(null)

  const submit = async (e: any) => {
    e.preventDefault()
    setLoading(true)
    setResp(null)
    const r = await fetch(`${API}/keywords/research`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ seeds: seeds.split(',').map(s => s.trim()), max_keywords: 120 })
    })
    const data = await r.json()
    setResp(data)
    setLoading(false)
  }

  return (
    <main style={{ maxWidth: 1000, margin: '40px auto', padding: 24 }}>
      <h1>Keyword Research</h1>
      <form onSubmit={submit}>
        <label>Seeds (comma separated)</label><br/>
        <input value={seeds} onChange={e => setSeeds(e.target.value)} style={{ width: '100%', padding: 8 }} />
        <button type="submit" disabled={loading} style={{ marginTop: 12 }}>{loading ? 'Running...' : 'Run'}</button>
      </form>
      {resp && (
        <pre style={{ marginTop: 20, background: '#111', color: '#0f0', padding: 12, overflow: 'auto' }}>{JSON.stringify(resp, null, 2)}</pre>
      )}
    </main>
  )
}

