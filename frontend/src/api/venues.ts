import client from './client'
import type { Venue } from '../types'

export function fetchVenues(params?: Record<string, string>) {
  return client.get<Venue[]>('/venues/', { params }).then((r) => r.data)
}

export function fetchVenue(id: number) {
  return client.get<Venue>(`/venues/${id}/`).then((r) => r.data)
}

export function fetchOwnerVenues() {
  return client.get<Venue[]>('/venues/owner/').then((r) => r.data)
}

export function createVenue(data: FormData) {
  return client.post<Venue>('/venues/', data).then((r) => r.data)
}

export function updateVenue(id: number, data: Partial<Venue>) {
  return client.patch<Venue>(`/venues/${id}/`, data).then((r) => r.data)
}
