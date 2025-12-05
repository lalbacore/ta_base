export interface CapabilityProvider {
  provider_id: string
  provider_name: string
  trust_score: number
  reputation: number
  total_invocations: number
  success_rate: number
  capabilities: string[]
}

export interface Capability {
  capability_id: string
  provider_id: string
  capability_type: string
  description: string
  price: number
  trust_score: number
  reputation: number
  tags: string[]
  invocation_count: number
  success_rate: number
  last_invoked?: string
}

export interface CapabilitySearchFilters {
  capability_type?: string
  min_trust_score?: number
  min_reputation?: number
  max_price?: number
  tags?: string[]
  provider_id?: string
}

export interface CapabilityMatchResult {
  capability: Capability
  match_score: number
  breakdown: {
    type_match: number
    trust_score: number
    reputation: number
    cost_score: number
  }
}
