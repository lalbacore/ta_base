export interface TrustMetrics {
  agent_id: string
  agent_name: string
  trust_score: number
  success_rate: number
  total_operations: number
  failed_operations: number
  security_incidents: number
  policy_violations: number
  last_updated: string
}

export interface TrustEvent {
  event_id: string
  agent_id: string
  event_type: 'success' | 'failure' | 'security_incident' | 'policy_violation'
  description: string
  impact: number
  timestamp: string
}

export interface TrustHistory {
  agent_id: string
  data_points: TrustDataPoint[]
}

export interface TrustDataPoint {
  timestamp: string
  trust_score: number
}
