import type { Venue, ServiceListing } from '../types'

export function formatPrice(value: string | number): string {
  const n = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(n)) return '0'
  return Math.round(n).toLocaleString()
}

export function classifyService(listing: ServiceListing): string {
  const text = [
    listing.title,
    listing.description,
    listing.category?.name || '',
    ...(listing.packages || []).map((p) => p.name),
    ...(listing.addons || []).map((a) => a.name),
  ]
    .join(' ')
    .toLowerCase()

  if (/photo|camera|candid/.test(text)) {
    if (/cinema|video|film|reel/.test(text)) return 'Cinematography'
    return 'Photography'
  }
  if (/cater|menu|buffet|food|dining/.test(text)) return 'Catering'
  if (/decor|floral|stage|styling|design/.test(text)) return 'Decorations'
  if (/light|led|rig/.test(text)) return 'Lighting'
  if (/dj|sound|music|audio|speaker/.test(text)) return 'Sound / DJ'
  return listing.category?.name || 'Individual service'
}

export function listingIcon(kind: 'venue' | 'service', label: string): string {
  const norm = (label || '').toLowerCase()
  if (kind === 'venue') {
    if (norm.includes('resort')) return 'fa-umbrella-beach'
    if (norm.includes('farm') || norm.includes('lawn') || norm.includes('outdoor')) return 'fa-tree'
    if (norm.includes('banquet') || norm.includes('hall')) return 'fa-champagne-glasses'
    return 'fa-hotel'
  }
  if (norm.includes('photo')) return 'fa-camera-retro'
  if (norm.includes('cinema') || norm.includes('video')) return 'fa-video'
  if (norm.includes('cater') || norm.includes('food')) return 'fa-utensils'
  if (norm.includes('decor')) return 'fa-wand-magic-sparkles'
  if (norm.includes('light')) return 'fa-lightbulb'
  if (norm.includes('sound') || norm.includes('dj') || norm.includes('music')) return 'fa-music'
  return 'fa-briefcase'
}

export function priceUnit(listing: ServiceListing): string {
  const m = listing.pricing_model
  if (m === 'PER_HOUR') return '/hour'
  if (m === 'PER_GUEST') return '/guest'
  if (m === 'CUSTOM_QUOTE') return '/quote'
  return '/event'
}

export function venuePriceValue(venue: Venue): number {
  return parseFloat(venue.base_price) || 0
}

export function servicePriceValue(listing: ServiceListing): number {
  return parseFloat(listing.base_price) || 0
}

export function venueLocation(venue: Venue): string {
  return [venue.city, venue.state].filter(Boolean).join(', ') || venue.address
}

export function sortResults<T>(
  items: T[],
  sort: string,
  getPrice: (item: T) => number,
  getDate: (item: T) => string,
): T[] {
  const sorted = [...items]
  switch (sort) {
    case 'price_low':
      sorted.sort((a, b) => getPrice(a) - getPrice(b))
      break
    case 'price_high':
      sorted.sort((a, b) => getPrice(b) - getPrice(a))
      break
    case 'newest':
      sorted.sort((a, b) => new Date(getDate(b)).getTime() - new Date(getDate(a)).getTime())
      break
    default:
      break
  }
  return sorted
}

export interface Tab {
  label: string
  icon: string
  href: string
  active: boolean
}

export function buildTabs(params: URLSearchParams): Tab[] {
  const city = params.get('city') || ''
  const area = params.get('area') || ''
  const q = params.get('q') || ''
  const category = params.get('category') || ''
  const sort = params.get('sort') || 'recommended'
  const availability = params.get('availability') || ''
  const kind = params.get('kind') || 'all'

  const base = (k: string, avail?: string) => {
    const sp = new URLSearchParams()
    if (city) sp.set('city', city)
    if (area) sp.set('area', area)
    if (q) sp.set('q', q)
    if (category) sp.set('category', category)
    if (sort !== 'recommended') sp.set('sort', sort)
    if (avail) sp.set('availability', avail)
    if (k !== 'all') sp.set('kind', k)
    const qs = sp.toString()
    return `/explore${qs ? '?' + qs : ''}`
  }

  return [
    { label: 'All', icon: 'fa-store', href: base('all'), active: kind === 'all' && !availability },
    { label: 'Venues', icon: 'fa-building', href: base('venues'), active: kind === 'venues' },
    { label: 'Services', icon: 'fa-camera', href: base('services'), active: kind === 'services' },
    {
      label: 'Available today',
      icon: 'fa-calendar-check',
      href: base(kind, availability ? '' : 'today'),
      active: !!availability,
    },
  ]
}

export const sortOptions = [
  { value: 'recommended', label: 'Recommended' },
  { value: 'price_low', label: 'Price: low to high' },
  { value: 'price_high', label: 'Price: high to low' },
  { value: 'newest', label: 'Newest' },
]

export const locationPresets = [
  { city: 'New York', area: '' },
  { city: 'Los Angeles', area: '' },
  { city: 'New York', area: 'Manhattan' },
]

export const serviceCategories = [
  'Photography', 'Catering', 'Decorations', 'Lighting', 'Sound / DJ', 'Cinematography',
]

export function buildVenueCard(venue: Venue) {
  const amenities = (venue.amenities || []).slice(0, 3).map((a) => a.name)
  const loc = venueLocation(venue)
  const tags = amenities.length > 0 ? amenities : [venue.venue_type, venue.city, 'Venue booking'].filter(Boolean).slice(0, 3)

  return {
    id: venue.id,
    kind: 'venue' as const,
    title: venue.name,
    typeLabel: loc,
    icon: listingIcon('venue', venue.venue_type || 'Venue'),
    description: venue.description || venue.address || loc,
    priceDisplay: formatPrice(venue.base_price),
    priceUnit: '/day',
    priceValue: venuePriceValue(venue),
    tags,
    href: `/book/?venue_id=${venue.id}`,
    img: venue.media?.[0]?.file || null,
    createdAt: venue.created_at,
  }
}

export function buildServiceCard(listing: ServiceListing) {
  const label = classifyService(listing)
  const pkgs = (listing.packages || []).map((p) => p.name)
  const ads = (listing.addons || []).map((a) => a.name)
  const tags = (pkgs.concat(ads)).slice(0, 3)
  if (tags.length === 0) tags.push(label, 'Approved listing')

  return {
    id: listing.id,
    kind: 'service' as const,
    title: listing.title,
    typeLabel: label,
    icon: listingIcon('service', label),
    description: listing.description || `${label} by ${listing.vendor?.business_name || ''}`,
    priceDisplay: formatPrice(listing.base_price),
    priceUnit: priceUnit(listing),
    priceValue: servicePriceValue(listing),
    tags,
    href: `/book/?service_id=${listing.id}`,
    img: listing.media?.[0]?.file || null,
    createdAt: listing.created_at,
    vendorName: listing.vendor?.business_name,
  }
}
