import { useState } from 'react'

const API = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function Home() {
  return (
    <main style={{ maxWidth: 900, margin: '40px auto', padding: 24 }}>
      <h1>SEO Workbench Dashboard</h1>
      <p>API: {API}</p>
      <ul>
        <li><a href="/research">Keyword Research</a></li>
        <li><a href="/brief">Content Brief</a></li>
        <li><a href="/generate">Generate Article</a></li>
      </ul>
    </main>
  )
}

