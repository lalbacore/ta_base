import apiClient from './api.client'
import type { Capability, Provider, RegistryStatistics, CapabilityFilters } from '@/types/registry.types'

export class RegistryService {
  async getAllCapabilities(filters?: CapabilityFilters): Promise<Capability[]> {
    const params = new URLSearchParams()
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    const response = await apiClient.get(`/registry/capabilities?${params.toString()}`)
    return response.data
  }

  async getCapability(capabilityId: string): Promise<Capability> {
    const response = await apiClient.get(`/registry/capability/${capabilityId}`)
    return response.data
  }

  async getAllProviders(): Promise<Provider[]> {
    const response = await apiClient.get('/registry/providers')
    return response.data
  }

  async getProvider(providerId: string): Promise<Provider> {
    const response = await apiClient.get(`/registry/provider/${providerId}`)
    return response.data
  }

  async getStatistics(): Promise<RegistryStatistics> {
    const response = await apiClient.get('/registry/statistics')
    return response.data
  }

  async revokeCapability(capabilityId: string): Promise<void> {
    await apiClient.post(`/registry/capability/${capabilityId}/revoke`)
  }
}

export default new RegistryService()
