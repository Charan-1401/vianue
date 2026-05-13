import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchVenues, fetchVenue, fetchOwnerVenues, createVenue } from '../api/venues'

export function useVenues(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['venues', params],
    queryFn: () => fetchVenues(params),
  })
}

export function useVenue(id: number | null) {
  return useQuery({
    queryKey: ['venue', id],
    queryFn: () => fetchVenue(id!),
    enabled: !!id,
  })
}

export function useOwnerVenues() {
  return useQuery({
    queryKey: ['owner-venues'],
    queryFn: fetchOwnerVenues,
  })
}

export function useCreateVenue() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createVenue,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['venues'] })
      queryClient.invalidateQueries({ queryKey: ['owner-venues'] })
    },
  })
}
