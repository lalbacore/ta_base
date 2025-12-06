import apiClient from './api.client'
import type { MissionSpec, WorkflowStatus } from '@/types/mission.types'
import type {
  AgentCard,
  DiscoveryParams,
  DiscoveryResponse,
  MatchCriteria,
  MatchResponse
} from '@/types/agent.types'

export class MissionService {
  async submitMission(mission: MissionSpec): Promise<{ mission_id: string }> {
    const response = await apiClient.post('/mission/submit', mission)
    return response.data
  }

  async getWorkflowStatus(workflowId: string): Promise<WorkflowStatus> {
    const response = await apiClient.get(`/mission/workflow/${workflowId}/status`)
    return response.data
  }

  async resumeWorkflow(workflowId: string): Promise<void> {
    await apiClient.post(`/mission/workflow/${workflowId}/resume`)
  }

  async approveBreakpoint(breakpointId: string, optionIndex: number): Promise<void> {
    await apiClient.post(`/mission/breakpoint/${breakpointId}/approve`, { option_index: optionIndex })
  }

  async rejectBreakpoint(breakpointId: string): Promise<void> {
    await apiClient.post(`/mission/breakpoint/${breakpointId}/reject`)
  }

  async listMissions(): Promise<MissionSpec[]> {
    const response = await apiClient.get('/mission/list')
    return response.data
  }

  async listWorkflows(): Promise<WorkflowStatus[]> {
    const response = await apiClient.get('/mission/workflow/list')
    return response.data
  }

  // ============================================================================
  // A2A Agent Discovery Methods
  // ============================================================================

  /**
   * Discover available agents from local and remote registries
   */
  async discoverAgents(params?: DiscoveryParams): Promise<DiscoveryResponse> {
    const queryParams = new URLSearchParams()

    if (params?.agent_type) {
      queryParams.append('agent_type', params.agent_type)
    }
    if (params?.min_trust_score !== undefined) {
      queryParams.append('min_trust_score', params.min_trust_score.toString())
    }
    if (params?.min_success_rate !== undefined) {
      queryParams.append('min_success_rate', params.min_success_rate.toString())
    }
    if (params?.use_cache !== undefined) {
      queryParams.append('use_cache', params.use_cache.toString())
    }

    const url = `/mission/discover-agents${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  }

  /**
   * Match agents to mission requirements with weighted scoring
   */
  async matchAgents(criteria: MatchCriteria): Promise<MatchResponse> {
    const response = await apiClient.post('/mission/match-agents', criteria)
    return response.data
  }

  /**
   * Get detailed information about a specific agent
   */
  async getAgentDetails(agentId: string): Promise<AgentCard> {
    const response = await apiClient.get(`/mission/agent/${agentId}`)
    return response.data
  }

  /**
   * Get all specialist agents
   */
  async getSpecialists(): Promise<DiscoveryResponse> {
    const response = await apiClient.get('/mission/agents/specialists')
    return response.data
  }

  /**
   * Get all role agents (Architect, Builder, Critic, etc.)
   */
  async getRoleAgents(): Promise<DiscoveryResponse> {
    const response = await apiClient.get('/mission/agents/roles')
    return response.data
  }

  /**
   * Clear agent discovery cache
   */
  async clearAgentCache(): Promise<void> {
    await apiClient.post('/mission/agents/clear-cache')
  }
}

export default new MissionService()
