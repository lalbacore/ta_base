export type CapabilityType =
  | 'code_generation'
  | 'security_audit'
  | 'testing'
  | 'data_analysis'
  | 'deployment'
  | 'documentation'
  | 'code_review'
  | 'monitoring'
  | 'refactoring'
  | 'database_design'
  | 'performance_optimization'
  | 'cicd'
  | 'api_integration'
  | 'machine_learning'

export interface Capability {
  capability_id: string
  capability_type: CapabilityType
  provider_id: string
  provider_name: string
  name: string
  description: string
  trust_score: number
  reputation: number
  price: number
  invocations: number
  success_rate: number
  tags: string[]
  created_at: string
  match_score?: number
}

export interface Provider {
  provider_id: string
  name: string
  type: CapabilityType
  trust_score: number
  total_capabilities: number
}

export interface RegistryStatistics {
  total_capabilities: number
  total_providers: number
  capabilities_by_type: Record<string, number>
  average_trust_score: number
  average_price: number
  average_reputation: number
  total_invocations: number
}

export interface CapabilityFilters {
  capability_type?: string
  min_trust_score?: number
  max_price?: number
  tags?: string
  search?: string
}
