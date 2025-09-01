import { useState } from 'react'

const API = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function Brief() {
  const [seed, setSeed] = useState('best hiking backpacks')
  const [keywords, setKeywords] = useState('hiking backpacks, ultralight backpack')
  const [loading, setLoading] = useState(false)
  const [resp, setResp] = useState<any>(null)

  const submit = async (e: any) => {
    e.preventDefault()
    setLoading(true)
    setResp(null)
    const r = await fetch(`${API}/content/brief`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ seed, keywords: keywords.split(',').map(s => s.trim()) })
    })
    const data = await r.json()
    setResp(data)
    setLoading(false)
  }

  return (
    <main style={{ maxWidth: 1000, margin: '40px auto', padding: 24 }}>
      <h1>Content Brief</h1>
      <form onSubmit={submit}>
        <label>Seed</label><br/>
        <input value={seed} onChange={e => setSeed(e.target.value)} style={{ width: '100%', padding: 8, marginBottom: 8 }} />
        <label>Keywords (comma separated)</label><br/>
        <input value={keywords} onChange={e => setKeywords(e.target.value)} style={{ width: '100%', padding: 8 }} />
        <button type="submit" disabled={loading} style={{ marginTop: 12 }}>{loading ? 'Building...' : 'Build Brief'}</button>
      </form>
      {resp && (
        <pre style={{ marginTop: 20, background: '#111', color: '#0f0', padding: 12, overflow: 'auto' }}>{JSON.stringify(resp, null, 2)}</pre>
      )}
    </main>
  )
}

