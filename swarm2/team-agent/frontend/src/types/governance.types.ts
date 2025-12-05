export interface PolicyConfig {
  min_trust_score: number
  require_security_review: boolean
  allowed_languages: string[]
  max_execution_time: number
  require_approval_below_trust: number
  auto_approve_threshold: number
  enable_breakpoints: boolean
}

export interface GovernanceDecision {
  decision_id: string
  workflow_id: string
  timestamp: string
  status: 'approved' | 'rejected'
  composite_score: number
  violations: string[]
  reasons: string[]
}

export interface ApprovalGate {
  gate_id: string
  workflow_id: string
  gate_type: 'human_review' | 'policy_check' | 'security_audit'
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  decision_details?: any
}

export interface PolicyAuditLog {
  event_id: string
  event_type: 'policy_updated' | 'decision_made' | 'gate_approved' | 'gate_rejected'
  timestamp: string
  user?: string
  details: any
}
