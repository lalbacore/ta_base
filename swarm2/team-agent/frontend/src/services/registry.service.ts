import apiClient from './api.client'
import type { Capability, CapabilityProvider, CapabilityMatchResult } from '@/types/registry.types'

export class RegistryService {
  async getCapabilities(filters?: any): Promise<Capability[]> {
    const response = await apiClient.get('/registry/capabilities', { params: filters })
    return response.data
  }

  async getProviders(): Promise<CapabilityProvider[]> {
    const response = await apiClient.get('/registry/providers')
    return response.data
  }

  async discoverCapabilities(requirements: any): Promise<Capability[]> {
    const response = await apiClient.post('/registry/discover', requirements)
    return response.data
  }

  async matchCapabilities(requirements: any): Promise<CapabilityMatchResult[]> {
    const response = await apiClient.post('/registry/match', requirements)
    return response.data
  }

  async revokeCapability(capabilityId: string): Promise<void> {
    await apiClient.post(`/registry/capability/${capabilityId}/revoke`)
  }

  async getCapability(capabilityId: string): Promise<Capability> {
    const response = await apiClient.get(`/registry/capability/${capabilityId}`)
    return response.data
  }

  async getProvider(providerId: string): Promise<CapabilityProvider> {
    const response = await apiClient.get(`/registry/provider/${providerId}`)
    return response.data
  }
}

export default new RegistryService()
