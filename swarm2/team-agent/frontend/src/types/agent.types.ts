/**
 * Agent2Agent (A2A) Protocol Types
 *
 * Types for agent discovery, matching, and selection.
 */

export interface AgentCard {
  agent_id: string
  agent_name: string
  agent_type: 'role' | 'specialist' | 'tool'
  description: string
  version: string

  // Capabilities
  capabilities: AgentCapability[]
  specialties: string[]
  supported_languages: string[]
  tags: string[]

  // Trust & Reputation
  trust_score: number
  total_invocations: number
  success_rate: number
  average_rating: number

  // Status
  status: 'active' | 'inactive' | 'deprecated'
  certificate_serial?: string
  trust_domain?: string

  // Metadata
  author?: string
  homepage?: string
  license: string
  registry_url: string
  created_at: string
  updated_at: string
}

export interface AgentCapability {
  capability_id: string
  capability_name: string
  capability_type: string
  description: string
  domains: string[]
  keywords?: string[]
  is_primary?: boolean
  priority?: number
  version?: string
  success_rate?: number
  times_used?: number
}

export interface DiscoveryParams {
  agent_type?: 'role' | 'specialist' | 'tool'
  min_trust_score?: number
  min_success_rate?: number
  use_cache?: boolean
}

export interface MatchCriteria {
  agent_type?: string
  capability_type?: string
  required_specialties?: string[]
  required_tags?: string[]
  required_languages?: string[]
  min_trust_score?: number
  min_success_rate?: number
  min_total_invocations?: number
  min_average_rating?: number
  trust_score_weight?: number
  success_rate_weight?: number
  experience_weight?: number
  rating_weight?: number
}

export interface AgentMatch {
  agent: AgentCard
  score: number
  match_reasons: string[]
}

export interface DiscoveryResponse {
  agents: AgentCard[]
  total: number
  timestamp: string
}

export interface MatchResponse {
  matches: AgentMatch[]
  total: number
  best_match: AgentMatch | null
  timestamp: string
}

export interface SelectedAgent {
  agent_id: string
  agent_name: string
  agent_type: string
  trust_score: number
  capabilities: string[]
  match_score?: number
}
