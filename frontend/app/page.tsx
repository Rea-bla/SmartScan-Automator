'use client'
import { useState } from 'react'

interface Result {
  site: string
  name: string
  price: number
  url: string
  image_url: string
}

export default function Home() {
  const [query, setQuery]     = useState('')
  const [results, setResults] = useState<Result[]>([])
  const [loading, setLoading] = useState(false)

  const search = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const res  = await fetch(`http://localhost:8000/api/v1/search?q=${encodeURIComponent(query)}`)
      const data = await res.json()
      setResults(data.results)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-2">Fiyat Karşılaştır</h1>
      <p className="text-gray-500 mb-8">10 siteden anlık fiyat karşılaştırması</p>

      <div className="flex gap-2 mb-8">
        <input
          className="flex-1 border border-gray-200 rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ürün adı veya model no..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && search()}
        />
        <button
          onClick={search}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
        >
          {loading ? 'Aranıyor...' : 'Ara'}
        </button>
      </div>

      {results.length > 0 && (
        <div className="flex flex-col gap-3">
          {results.map((r, i) => (
            <a key={i} href={r.url} target="_blank" rel="noreferrer"
               className="flex items-center gap-4 p-4 border border-gray-100 rounded-xl hover:border-blue-200 transition">
              {r.image_url && (
                <img src={r.image_url} alt="" className="w-14 h-14 object-contain rounded" />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{r.name}</p>
                <p className="text-xs text-gray-400 mt-0.5">{r.site}</p>
              </div>
              <p className="text-blue-600 font-bold whitespace-nowrap">
                {r.price.toLocaleString('tr-TR')} TL
              </p>
            </a>
          ))}
        </div>
      )}
    </main>
  )
}