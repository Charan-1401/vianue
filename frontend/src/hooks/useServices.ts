import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchServices, fetchService, fetchVendorServices, createService } from '../api/services'

export function useServices(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['services', params],
    queryFn: () => fetchServices(params),
  })
}

export function useService(id: number | null) {
  return useQuery({
    queryKey: ['service', id],
    queryFn: () => fetchService(id!),
    enabled: !!id,
  })
}

export function useVendorServices() {
  return useQuery({
    queryKey: ['vendor-services'],
    queryFn: fetchVendorServices,
  })
}

export function useCreateService() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createService,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] })
      queryClient.invalidateQueries({ queryKey: ['vendor-services'] })
    },
  })
}
