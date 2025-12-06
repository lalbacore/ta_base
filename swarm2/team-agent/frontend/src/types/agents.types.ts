export interface AgentCard {
  agent_id: string
  agent_name: string
  agent_type: string
  description: string
  capabilities: string[]
  module_path: string
  class_name: string
  trust_domain: string
  trust_score: number
  total_invocations: number
  success_rate: number
  status: string
  version: string
  created_at: string
  updated_at: string
}

export interface AgentInvocation {
  invocation_id: string
  agent_id: string
  workflow_id: string
  started_at: string
  completed_at: string
  duration: number
  status: 'success' | 'failure'
  error_message?: string
  output_data: Record<string, any>
}

export interface AgentStats {
  total_invocations: number
  successful_invocations: number
  failed_invocations: number
  success_rate: number
  trust_score: number
  average_duration: number
}

export interface AgentDetail {
  agent: AgentCard
  recent_invocations: AgentInvocation[]
  stats: AgentStats
}

export interface AgentsListResponse {
  agents: AgentCard[]
  total: number
  summary: {
    by_type: Record<string, number>
    by_domain: Record<string, number>
    by_status: Record<string, number>
  }
}

export interface InvocationsResponse {
  invocations: AgentInvocation[]
  total: number
  limit: number
  offset: number
}

export interface DiscoverAgentsRequest {
  capabilities?: string[]
  trust_domain?: string
  min_trust_score?: number
}

export interface DiscoverAgentsResponse {
  agents: AgentCard[]
  matches: number
}

export interface SystemStatsResponse {
  total_agents: number
  total_invocations: number
  average_trust_score: number
  top_agents: AgentCard[]
  recent_activity: AgentInvocation[]
}
