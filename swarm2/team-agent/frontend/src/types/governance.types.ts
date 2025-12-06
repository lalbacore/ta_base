export interface Policy {
  id: number
  name: string
  description: string | null
  is_active: boolean
  min_trust_score: number
  require_security_review: boolean
  allowed_languages: string[]
  max_cost_per_mission: number
  require_code_review: boolean
  auto_approve_threshold: number
  enable_breakpoints: boolean
  created_at: string
  updated_at: string
}

export interface PolicyConfig {
  id?: number
  name?: string
  description?: string | null
  is_active?: boolean
  min_trust_score: number
  require_security_review: boolean
  allowed_languages: string[]
  max_cost_per_mission: number
  require_code_review: boolean
  auto_approve_threshold: number
  enable_breakpoints: boolean
  created_at?: string
  updated_at?: string
}

export interface GovernanceDecision {
  decision_id: string
  workflow_id: string
  stage: string
  decision: 'approved' | 'rejected'
  timestamp: string
  trust_score: number
  policy_violations: number
  reason: string
}

export interface ComplianceViolation {
  policy: string
  required: any
  actual: any
  message: string
}

export interface ComplianceSatisfied {
  policy: string
  message: string
}

export interface ComplianceWarning {
  policy: string
  message: string
}

export interface ComplianceReport {
  status: 'fully_compliant' | 'compliant_with_warnings' | 'non_compliant'
  compliance_score: number
  violations: ComplianceViolation[]
  satisfied: ComplianceSatisfied[]
  warnings: ComplianceWarning[]
  summary: {
    total_checks: number
    violations_count: number
    satisfied_count: number
    warnings_count: number
  }
}
