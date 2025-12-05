import apiClient from './api.client'
import type { TrustMetrics, TrustEvent, TrustHistory } from '@/types/trust.types'

export class TrustService {
  async getAllAgents(): Promise<TrustMetrics[]> {
    const response = await apiClient.get('/trust/agents')
    return response.data
  }

  async getAgentDetails(agentId: string): Promise<TrustMetrics> {
    const response = await apiClient.get(`/trust/agent/${agentId}`)
    return response.data
  }

  async getAgentHistory(agentId: string): Promise<TrustHistory> {
    const response = await apiClient.get(`/trust/agent/${agentId}/history`)
    return response.data
  }

  async getAgentEvents(agentId: string): Promise<TrustEvent[]> {
    const response = await apiClient.get(`/trust/agent/${agentId}/events`)
    return response.data
  }

  async recordEvent(agentId: string, eventData: Partial<TrustEvent>): Promise<void> {
    await apiClient.post(`/trust/agent/${agentId}/event`, eventData)
  }
}

export default new TrustService()
