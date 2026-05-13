export interface User {
  id: number
  username: string
  email: string
  role: 'CUSTOMER' | 'OWNER' | 'VENDOR' | 'ADMIN'
  first_name: string
  last_name: string
  phone: string | null
  is_staff: boolean
}

export interface Amenity {
  id: number
  name: string
}

export interface VenueMedia {
  id: number
  file: string
  is_video: boolean
  description: string
  created_at: string
}

export interface Venue {
  id: number
  owner: number
  owner_name: string
  owner_username: string
  owner_phone: string | null
  name: string
  venue_type: string
  description: string
  address: string
  city: string
  state: string
  country: string
  pincode: string
  capacity_min: number
  capacity_max: number
  base_price: string
  status: string
  amenities: Amenity[]
  media: VenueMedia[]
  created_at: string
  updated_at: string
}

export interface VendorProfile {
  id: number
  user: number
  user_name: string
  user_username: string
  business_name: string
  phone: string | null
  bio: string
  is_verified: boolean
  cities: string[]
  created_at: string
}

export interface ServiceCategory {
  id: number
  name: string
}

export interface ServicePackage {
  id: number
  name: string
  description: string
  price: string
}

export interface ServiceAddOn {
  id: number
  name: string
  description: string
  price: string
}

export interface ServiceMedia {
  id: number
  file: string
  is_video: boolean
  description: string
  created_at: string
}

export interface ServiceListing {
  id: number
  vendor: VendorProfile
  title: string
  description: string
  base_price: string
  pricing_model: string
  min_order_value: string | null
  max_guests_supported: number | null
  status: string
  category: ServiceCategory
  packages: ServicePackage[]
  addons: ServiceAddOn[]
  media: ServiceMedia[]
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access: string
  refresh: string
}
