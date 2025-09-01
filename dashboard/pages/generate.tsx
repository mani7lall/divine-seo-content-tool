import { useState } from 'react'

const API = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function Generate() {
  const [topic, setTopic] = useState('best hiking backpacks')
  const [length, setLength] = useState(1500)
  const [loading, setLoading] = useState(false)
  const [resp, setResp] = useState<any>(null)

  const submit = async (e: any) => {
    e.preventDefault()
    setLoading(true)
    setResp(null)
    const r = await fetch(`${API}/content/generate`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, target_length_words: Number(length) })
    })
    const data = await r.json()
    setResp(data)
    setLoading(false)
  }

  return (
    <main style={{ maxWidth: 1000, margin: '40px auto', padding: 24 }}>
      <h1>Generate Article</h1>
      <form onSubmit={submit}>
        <label>Topic</label><br/>
        <input value={topic} onChange={e => setTopic(e.target.value)} style={{ width: '100%', padding: 8, marginBottom: 8 }} />
        <label>Target length (words)</label><br/>
        <input type="number" value={length} onChange={e => setLength(Number(e.target.value))} style={{ width: '100%', padding: 8 }} />
        <button type="submit" disabled={loading} style={{ marginTop: 12 }}>{loading ? 'Generating...' : 'Generate'}</button>
      </form>
      {resp && (
        <>
          <h3 style={{ marginTop: 24 }}>Title: {resp.title}</h3>
          <div style={{ whiteSpace: 'pre-wrap', background: '#111', color: '#0f0', padding: 12, overflow: 'auto' }}>
            {resp.article_markdown}
          </div>
        </>
      )}
    </main>
  )
}

