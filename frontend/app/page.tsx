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
  'n11':              'bg-green-100 text-green-700'
}

const STORAGE_OPTIONS = ['64 GB', '128 GB', '256 GB', '512 GB', '1 TB']
const SITE_OPTIONS = ['Trendyol', 'Hepsiburada', 'Amazon TR', 'MediaMarkt', 'Vatan Bilgisayar', 'Teknosa', 'n11']

function FilterSection({ title, isOpen, onToggle, children, badgeCount }: {
  title: string
  isOpen: boolean
  onToggle: () => void
  children: React.ReactNode
  badgeCount?: number
}) {
  return (
    <div className="border-b border-gray-200">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between py-3 text-left hover:text-blue-600 transition"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-800">{title}</span>
          {badgeCount !== undefined && badgeCount > 0 && (
            <span className="bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center leading-none">
              {badgeCount}
            </span>
          )}
        </div>
        <span className="text-gray-400 text-xs">{isOpen ? '▲' : '▼'}</span>
      </button>
      {isOpen && (
        <div className="pb-4">
          {children}
        </div>
      )}
    </div>
  )
}

export default function Home() {
  const [query, setQuery]       = useState('')
  const [results, setResults]   = useState<Result[]>([])
  const [loading, setLoading]   = useState(false)
  const [searched, setSearched] = useState(false)

  const [selectedStorage, setSelectedStorage] = useState<string>('')
  const [selectedSites, setSelectedSites]     = useState<string[]>([])
  const [sortOrder, setSortOrder]             = useState<'asc' | 'desc'>('asc')
  const [minPrice, setMinPrice]               = useState('')
  const [maxPrice, setMaxPrice]               = useState('')

  const [openSite, setOpenSite]       = useState(true)
  const [openPrice, setOpenPrice]     = useState(true)
  const [openStorage, setOpenStorage] = useState(false)

  const search = async () => {
    if (!query.trim()) return
    setLoading(true)
    setSearched(true)
    setResults([])
    try {
      const fullQuery = selectedStorage
        ? `${query.trim()} ${selectedStorage}`
        : query.trim()
      const res = await fetch(
        `http://127.0.0.1:8000/api/v1/search?q=${encodeURIComponent(fullQuery)}&limit=200`
      )
      if (!res.ok) {
        console.error('API hatasi:', res.status)
        return
      }
      const data = await res.json()
      setResults(data?.results || [])
    } catch (e) {
      console.error('Arama hatasi:', e)
    } finally {
      setLoading(false)
    }
  }

  const filteredResults = results
    .filter(r => {
      if (selectedSites.length > 0 && !selectedSites.includes(r.site)) return false
      if (minPrice && r.price < parseFloat(minPrice)) return false
      if (maxPrice && r.price > parseFloat(maxPrice)) return false
      if (selectedStorage && !r.name.toLowerCase().includes(selectedStorage.toLowerCase())) return false
      return true
    })
    .sort((a, b) => sortOrder === 'asc' ? a.price - b.price : b.price - a.price)

  const toggleSite = (site: string) => {
    setSelectedSites(prev =>
      prev.includes(site) ? prev.filter(s => s !== site) : [...prev, site]
    )
  }

  const handleClick = (url: string) => {
    if (!url || url.trim() === '') return
    const fullUrl = url.startsWith('http') ? url : 'https://' + url
    window.open(fullUrl, '_blank', 'noopener,noreferrer')
  }

  const formatPrice = (price: number) =>
    price.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

  const hasActiveFilters = selectedSites.length > 0 || selectedStorage || minPrice || maxPrice

  return (
    <div className="min-h-screen bg-white">

      {/* HEADER */}
      <header className="border-b border-gray-200 bg-white px-8 py-4">
        <div className="max-w-7xl mx-auto flex items-center gap-6">
          <h1 className="text-xl font-bold text-gray-900 whitespace-nowrap">SmartScan Automator</h1>
          <div className="flex-1 flex gap-2">
            <input
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-400"
              placeholder="Ürün adı veya model no..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && search()}
            />
            <button
              onClick={search}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-medium disabled:opacity-50 transition whitespace-nowrap"
            >
              {loading ? 'Aranıyor...' : 'Ara'}
            </button>
          </div>
        </div>
      </header>

      {/* BODY */}
      <div className="max-w-7xl mx-auto flex min-h-screen">

        {/* SOL FILTRE */}
        <aside className="w-[240px] min-w-[240px] flex-shrink-0 border-r border-gray-200 px-5 pt-6">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm font-bold text-gray-900">Filtreler</p>
            {hasActiveFilters && (
              <button
                onClick={() => {
                  setSelectedSites([])
                  setSelectedStorage('')
                  setMinPrice('')
                  setMaxPrice('')
                }}
                className="text-xs text-blue-600 hover:text-blue-800 transition"
              >
                Temizle
              </button>
            )}
          </div>

          <FilterSection
            title="Site"
            isOpen={openSite}
            onToggle={() => setOpenSite(p => !p)}
            badgeCount={selectedSites.length}
          >
            <div className="flex flex-col gap-2">
              {SITE_OPTIONS.map(site => (
                <label key={site} className="flex items-center gap-2 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={selectedSites.includes(site)}
                    onChange={() => toggleSite(site)}
                    className="accent-blue-600 w-4 h-4"
                  />
                  <span className="text-sm text-gray-700 group-hover:text-blue-600 transition">{site}</span>
                </label>
              ))}
            </div>
          </FilterSection>

          <FilterSection
            title="Fiyat & Sıralama"
            isOpen={openPrice}
            onToggle={() => setOpenPrice(p => !p)}
            badgeCount={(minPrice || maxPrice) ? 1 : 0}
          >
            <div className="flex flex-col gap-3">
              <div className="flex gap-2">
                <div className="flex-1">
                  <p className="text-xs text-gray-500 mb-1">Min TL</p>
                  <input
                    type="number"
                    placeholder="0"
                    value={minPrice}
                    onChange={e => setMinPrice(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-sm outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                  />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-gray-500 mb-1">Max TL</p>
                  <input
                    type="number"
                    placeholder="∞"
                    value={maxPrice}
                    onChange={e => setMaxPrice(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-sm outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                  />
                </div>
              </div>
              <div className="flex gap-1">
                {(['asc', 'desc'] as const).map(val => (
                  <button
                    key={val}
                    onClick={() => setSortOrder(val)}
                    className={`flex-1 px-2 py-1.5 rounded-lg text-xs font-medium border transition ${
                      sortOrder === val
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
                    }`}
                  >
                    {val === 'asc' ? '↑ En Ucuz' : '↓ En Pahalı'}
                  </button>
                ))}
              </div>
            </div>
          </FilterSection>

          <FilterSection
            title="Depolama"
            isOpen={openStorage}
            onToggle={() => setOpenStorage(p => !p)}
            badgeCount={selectedStorage ? 1 : 0}
          >
            <div className="flex flex-col gap-2">
              {STORAGE_OPTIONS.map(opt => (
                <label key={opt} className="flex items-center gap-2 cursor-pointer group">
                  <input
                    type="radio"
                    name="storage"
                    checked={selectedStorage === opt}
                    onChange={() => setSelectedStorage(opt)}
                    onClick={() => selectedStorage === opt && setSelectedStorage('')}
                    className="accent-blue-600 w-4 h-4"
                  />
                  <span className="text-sm text-gray-700 group-hover:text-blue-600 transition">{opt}</span>
                </label>
              ))}
            </div>
          </FilterSection>
        </aside>

        {/* SAG ICERIK */}
        <main className="flex-1 min-w-0 px-8 pt-6 pb-10">

          {!searched && !loading && (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <p className="text-4xl mb-4">🔍</p>
              <p className="text-lg font-semibold text-gray-700">Ne aramak istersiniz?</p>
              <p className="text-sm text-gray-400 mt-1">
                7 farklı siteden aynı anda fiyat karşılaştırması yapın
              </p>
            </div>
          )}

          {loading && (
            <div className="flex flex-col gap-3">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="flex items-center gap-4 p-4 border border-gray-100 rounded-xl animate-pulse bg-white">
                  <div className="w-16 h-16 bg-gray-200 rounded-lg flex-shrink-0" />
                  <div className="flex-1 min-w-0 space-y-2">
                    <div className="h-3 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-200 rounded w-1/3" />
                  </div>
                  <div className="h-5 bg-gray-200 rounded w-24 flex-shrink-0" />
                </div>
              ))}
            </div>
          )}

          {!loading && searched && filteredResults.length === 0 && (
            <div className="text-center py-20 text-gray-400">
              <p className="text-5xl mb-4">😕</p>
              <p className="text-lg font-medium text-gray-600">Sonuç bulunamadı</p>
              <p className="text-sm mt-1">Farklı bir ürün adı deneyin veya filtreleri genişletin</p>
            </div>
          )}

          {!loading && filteredResults.length > 0 && (
            <>
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm text-gray-500">
                  <span className="font-semibold text-gray-800">{query}</span>
                  {selectedStorage && <span className="text-blue-600"> · {selectedStorage}</span>}
                  <span className="ml-2 text-gray-400">{filteredResults.length} sonuç</span>
                </p>
                <p className="text-xs text-gray-400">
                  {sortOrder === 'asc' ? 'En ucuzdan pahalıya' : 'En pahalıdan ucuza'}
                </p>
              </div>

              <div className="flex flex-col gap-3">
                {filteredResults.map((r, i) => (
                  <div
                    key={i}
                    onClick={() => handleClick(r.url)}
                    className="flex items-center gap-4 p-4 border border-gray-200 rounded-xl hover:border-blue-400 hover:shadow-md transition cursor-pointer bg-white"
                  >
                    <div className="w-16 h-16 flex-shrink-0 bg-gray-50 rounded-lg flex items-center justify-center">
                      {r.image_url ? (
                        <img
                          src={r.image_url}
                          alt={r.name}
                          className="w-full h-full object-contain rounded-lg"
                          onError={e => { (e.target as HTMLImageElement).style.display = 'none' }}
                        />
                      ) : (
                        <span className="text-gray-300 text-xs">Görsel yok</span>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{r.name}</p>
                      <span className={`inline-block text-xs px-2 py-0.5 rounded-full mt-1 font-medium ${SITE_COLORS[r.site] || 'bg-gray-100 text-gray-600'}`}>
                        {r.site}
                      </span>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p className="text-blue-600 font-bold text-base whitespace-nowrap">
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
      </div>
    </div>
  )
}