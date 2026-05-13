import client from './client'
import type { ServiceListing } from '../types'

export function fetchServices(params?: Record<string, string>) {
  return client.get<ServiceListing[]>('/services/', { params }).then((r) => r.data)
}

export function fetchService(id: number) {
  return client.get<ServiceListing>(`/services/${id}/`).then((r) => r.data)
}

export function fetchVendorServices() {
  return client.get<ServiceListing[]>('/services/vendor/').then((r) => r.data)
}

export function createService(data: FormData) {
  return client.post<ServiceListing>('/services/', data).then((r) => r.data)
}
