'use client'
import { useState } from 'react'

interface Result {
  site: string
  name: string
  price: number
  url: string
  image_url: string
}

const SITE_COLORS: Record<string, string> = {
  'Trendyol':         'bg-orange-100 text-orange-700',
  'Hepsiburada':      'bg-blue-100 text-blue-700',
  'Amazon TR':        'bg-yellow-100 text-yellow-700',
  'MediaMarkt':       'bg-red-100 text-red-700',
  'Vatan Bilgisayar': 'bg-indigo-100 text-indigo-700',
  'Teknosa':          'bg-amber-100 text-amber-700',
}

export default function Home() {
  const [query, setQuery]   = useState('')
  const [results, setResults] = useState<Result[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const search = async () => {
    if (!query.trim()) return
    setLoading(true)
    setSearched(true)
    setResults([])
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/v1/search?q=${encodeURIComponent(query)}&limit=`
      )
      const data = await res.json()
      setResults(data.results || [])
    } catch (e) {
      console.error('Arama hatasi:', e)
    } finally {
      setLoading(false)
    }
  }

  const handleClick = (url: string) => {
    if (!url || url.trim() === '') return
    // URL gecerli mi kontrol et
    const fullUrl = url.startsWith('http') ? url : 'https://' + url
    window.open(fullUrl, '_blank', 'noopener,noreferrer')
  }

  const formatPrice = (price: number) => {
    return price.toLocaleString('tr-TR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  }

  return (
    <main className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-1">SmartScan Automator</h1>
      <p className="text-gray-500 mb-8 text-sm">
        6 Farklı siteden aynı anda fiyat karşılaştırması yapın. Aradığınız ürünün adını yazın, gerisini bize bırakın! En uygun fiyatı ve satıcıyı saniyeler içinde bulun.
      </p>

      <div className="flex gap-2 mb-8">
        <input
          className="flex-1 border border-gray-200 rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Urun adi veya model no..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && search()}
        />
        <button
          onClick={search}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-50 transition"
        >
          {loading ? 'Aranıyor...' : 'Ara'}
        </button>
      </div>

      {/* Yukleniyor */}
      {loading && (
        <div className="flex flex-col gap-3">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-4 p-4 border border-gray-100 rounded-xl animate-pulse"
            >
              <div className="w-14 h-14 bg-gray-200 rounded" />
              <div className="flex-1 space-y-2">
                <div className="h-3 bg-gray-200 rounded w-3/4" />
                <div className="h-3 bg-gray-200 rounded w-1/4" />
              </div>
              <div className="h-4 bg-gray-200 rounded w-20" />
            </div>
          ))}
        </div>
      )}

      {/* Sonuc yok */}
      {!loading && searched && results.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg">Sonuc bulunamadi</p>
          <p className="text-sm mt-1">Farkli bir urun adi deneyin</p>
        </div>
      )}

      {/* Sonuclar */}
      {!loading && results.length > 0 && (
        <>
          <p className="text-sm text-gray-400 mb-3">
            {results.length} sonuc bulundu — fiyata gore sirali
          </p>
          <div className="flex flex-col gap-3">
            {results.map((r, i) => (
              <div
                key={i}
                onClick={() => handleClick(r.url)}
                className="flex items-center gap-4 p-4 border border-gray-100 rounded-xl hover:border-blue-300 hover:shadow-sm transition cursor-pointer"
              >
                {/* Resim */}
                <div className="w-14 h-14 flex-shrink-0">
                  {r.image_url ? (
                    <img
                      src={r.image_url}
                      alt={r.name}
                      className="w-full h-full object-contain rounded"
                      onError={e => {
                        (e.target as HTMLImageElement).style.display = 'none'
                      }}
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-100 rounded flex items-center justify-center text-gray-300 text-xs">
                      Gorsel yok
                    </div>
                  )}
                </div>

                {/* Isim ve site */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{r.name}</p>
                  <span
                    className={`inline-block text-xs px-2 py-0.5 rounded-full mt-1 font-medium ${
                      SITE_COLORS[r.site] || 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {r.site}
                  </span>
                </div>

                {/* Fiyat */}
                <div className="text-right flex-shrink-0">
                  <p className="text-blue-600 font-bold text-sm whitespace-nowrap">
                    {formatPrice(r.price)} TL
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">Siteye git →</p>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </main>
  )
}