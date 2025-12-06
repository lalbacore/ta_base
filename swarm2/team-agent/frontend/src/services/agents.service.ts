import apiClient from './api.client'
import type {
  AgentCard,
  AgentDetail,
  AgentsListResponse,
  InvocationsResponse,
  DiscoverAgentsRequest,
  DiscoverAgentsResponse,
  SystemStatsResponse
} from '@/types/agents.types'

export class AgentsService {
  /**
   * Get all registered agents with optional filtering
   */
  async listAgents(filters?: {
    type?: string
    domain?: string
    status?: string
  }): Promise<AgentsListResponse> {
    const params = new URLSearchParams()
    if (filters?.type) params.append('type', filters.type)
    if (filters?.domain) params.append('domain', filters.domain)
    if (filters?.status) params.append('status', filters.status)

    const response = await apiClient.get(`/agents?${params.toString()}`)
    return response.data
  }

  /**
   * Get detailed information about a specific agent
   */
  async getAgent(agentId: string): Promise<AgentDetail> {
    const response = await apiClient.get(`/agents/${agentId}`)
    return response.data
  }

  /**
   * Get invocation history for a specific agent
   */
  async getAgentInvocations(
    agentId: string,
    options?: {
      limit?: number
      offset?: number
      status?: 'success' | 'failure'
    }
  ): Promise<InvocationsResponse> {
    const params = new URLSearchParams()
    if (options?.limit) params.append('limit', options.limit.toString())
    if (options?.offset) params.append('offset', options.offset.toString())
    if (options?.status) params.append('status', options.status)

    const response = await apiClient.get(`/agents/${agentId}/invocations?${params.toString()}`)
    return response.data
  }

  /**
   * Discover agents by capabilities or requirements
   */
  async discoverAgents(request: DiscoverAgentsRequest): Promise<DiscoverAgentsResponse> {
    const response = await apiClient.post('/agents/discover', request)
    return response.data
  }

  /**
   * Get overall agent system statistics
   */
  async getSystemStats(): Promise<SystemStatsResponse> {
    const response = await apiClient.get('/agents/stats')
    return response.data
  }
}

export default new AgentsService()
