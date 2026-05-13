import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useVenues } from '../hooks/useVenues'
import { useServices } from '../hooks/useServices'
import ExploreCard from '../components/ExploreCard'
import {
  buildVenueCard, buildServiceCard,
  buildTabs, sortOptions, locationPresets,
} from '../utils/explore'
import type { Venue, ServiceListing } from '../types'

interface CardData {
  kind: 'venue' | 'service'
  id: number
  title: string
  typeLabel: string
  icon: string
  description: string
  priceDisplay: string
  priceUnit: string
  priceValue: number
  tags: string[]
  href: string
  img: string | null
  createdAt: string
  vendorName?: string
}

export default function Explore() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [searchInput, setSearchInput] = useState(searchParams.get('q') || '')

  const kind = searchParams.get('kind') || 'all'
  const city = searchParams.get('city') || ''
  const area = searchParams.get('area') || ''
  const q = searchParams.get('q') || ''
  const sort = searchParams.get('sort') || 'recommended'
  const availability = searchParams.get('availability') || ''

  const apiParams: Record<string, string> = {}
  if (q) apiParams.search = q
  if (city) apiParams.city = city
  if (area) apiParams.area = area
  if (availability) apiParams.available_today = 'true'
  if (sort === 'price_low') apiParams.ordering = 'base_price'
  else if (sort === 'price_high') apiParams.ordering = '-base_price'
  else if (sort === 'newest') apiParams.ordering = '-created_at'

  const venuesQuery = useVenues(kind !== 'services' ? apiParams : undefined)
  const servicesQuery = useServices(kind !== 'venues' ? apiParams : undefined)

  const isLoading = venuesQuery.isLoading || servicesQuery.isLoading
  const isError = venuesQuery.isError || servicesQuery.isError

  const venues: Venue[] = Array.isArray(venuesQuery.data) ? venuesQuery.data : []
  const services: ServiceListing[] = Array.isArray(servicesQuery.data) ? servicesQuery.data : []

  const venueCards: CardData[] = venues.map(buildVenueCard)
  const serviceCards: CardData[] = services.map(buildServiceCard)

  let displayCards: CardData[]
  if (kind === 'venues') {
    displayCards = venueCards
  } else if (kind === 'services') {
    displayCards = serviceCards
  } else {
    displayCards = [...venueCards, ...serviceCards]
  }

  if (displayCards.length > 0) {
    if (sort === 'price_low') {
      displayCards.sort((a, b) => a.priceValue - b.priceValue)
    } else if (sort === 'price_high') {
      displayCards.sort((a, b) => b.priceValue - a.priceValue)
    } else if (sort === 'newest') {
      displayCards.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    }
  }

  const tabs = buildTabs(searchParams)
  const resultsCount = displayCards.length
  const resultsLabel = area || city || 'all listings'

  const updateParams = (updates: Record<string, string>) => {
    const next = new URLSearchParams(searchParams)
    for (const [k, v] of Object.entries(updates)) {
      if (v) next.set(k, v)
      else next.delete(k)
    }
    setSearchParams(next, { replace: true })
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    updateParams({ q: searchInput })
  }

  const setSort = (value: string) => updateParams({ sort: value })
  const setLocation = (c: string, a: string) => {
    const next = new URLSearchParams(searchParams)
    if (c) { next.set('city', c) } else { next.delete('city') }
    if (a) { next.set('area', a) } else { next.delete('area') }
    setSearchParams(next, { replace: true })
  }

  return (
    <section className="explore-page">
      <div className="explore-toolbar">
        <form className="explore-search" onSubmit={handleSearch}>
          <i className="fas fa-search explore-search-icon" />
          <input
            type="text"
            placeholder="Search venues and services..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="explore-search-input"
          />
        </form>

        <div className="explore-filters">
          <div className="explore-location">
            <select
              value={city}
              onChange={(e) => setLocation(e.target.value, area)}
              className="explore-select"
            >
              <option value="">All cities</option>
              {locationPresets.map((p) => (
                <option key={p.city + p.area} value={p.city}>
                  {p.city}{p.area ? ` (${p.area})` : ''}
                </option>
              ))}
            </select>
          </div>

          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="explore-select"
          >
            {sortOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="explore-tabs">
        {tabs.map((tab) => (
          <a
            key={tab.label}
            href={tab.href}
            onClick={(e) => {
              e.preventDefault()
              const qs = tab.href.split('?')[1] || ''
              setSearchParams(new URLSearchParams(qs), { replace: true })
            }}
            className={`explore-tab ${tab.active ? 'is-active' : ''}`}
          >
            <i className={`fas ${tab.icon}`} />
            {tab.label}
          </a>
        ))}
      </div>

      {isLoading && <div className="loading-screen">Loading...</div>}
      {isError && <div className="loading-screen">Failed to load results.</div>}
      {!isLoading && !isError && resultsCount === 0 && (
        <div className="loading-screen">
          <p>No results found for {resultsLabel}. Try adjusting your filters.</p>
        </div>
      )}

      {!isLoading && !isError && resultsCount > 0 && (
        <>
          <p className="explore-meta">
            {resultsCount} result{resultsCount !== 1 ? 's' : ''} in <strong>{resultsLabel}</strong>
          </p>

          <div className="results-grid">
            {displayCards.map((card) => (
              <ExploreCard key={`${card.kind}-${card.id}`} {...card} />
            ))}
          </div>
        </>
      )}
    </section>
  )
}
