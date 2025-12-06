export interface CapabilityRequirement {
  capability_type: string
  min_trust_score?: number
  max_cost?: number
  required_tags?: string[]
}

export enum BreakpointType {
  CAPABILITY_SELECTION = 'capability_selection',
  DESIGN_APPROVAL = 'design_approval',
  BUILD_APPROVAL = 'build_approval',
  REVIEW_APPROVAL = 'review_approval',
  GOVERNANCE_APPROVAL = 'governance_approval'
}

export interface MissionSpec {
  mission_id: string
  description: string
  required_capabilities: CapabilityRequirement[]
  selected_agents?: string[]  // Optional: pre-selected agent IDs for mission
  max_cost?: number
  min_trust_score: number
  breakpoints: BreakpointType[]
  auto_approve_trusted: boolean
  auto_approve_threshold: number
}

export interface WorkflowStatus {
  workflow_id: string
  mission_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused'
  current_stage: string
  progress: number
  stages: WorkflowStage[]
  created_at: string
  updated_at: string
}

export interface WorkflowStage {
  stage_name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  output?: any
}

export interface Breakpoint {
  breakpoint_id: string
  workflow_id: string
  breakpoint_type: BreakpointType
  options: CapabilityMatch[]
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
}

export interface CapabilityMatch {
  provider_id: string
  capability_id: string
  match_score: number
  trust_score: number
  price: number
  details: any
}
