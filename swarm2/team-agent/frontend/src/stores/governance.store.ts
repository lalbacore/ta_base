import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PolicyConfig, GovernanceDecision, ApprovalGate, PolicyAuditLog } from '@/types/governance.types'

export const useGovernanceStore = defineStore('governance', () => {
  // State
  const policyConfig = ref<PolicyConfig>({
    min_trust_score: 75,
    require_security_review: true,
    allowed_languages: ['python', 'typescript', 'javascript'],
    max_execution_time: 3600,
    require_approval_below_trust: 60,
    auto_approve_threshold: 90,
    enable_breakpoints: true
  })
  const decisions = ref<GovernanceDecision[]>([])
  const approvalGates = ref<ApprovalGate[]>([])
  const auditLog = ref<PolicyAuditLog[]>([])

  // Getters
  const pendingGates = computed(() =>
    approvalGates.value.filter(g => g.status === 'pending')
  )

  const recentDecisions = computed(() =>
    decisions.value.slice(0, 50)
  )

  const approvalRate = computed(() => {
    if (decisions.value.length === 0) return 0
    const approved = decisions.value.filter(d => d.status === 'approved').length
    return (approved / decisions.value.length) * 100
  })

  // Actions
  async function fetchPolicyConfig(): Promise<void> {
    // TODO: API call
  }

  async function updatePolicyConfig(config: Partial<PolicyConfig>): Promise<void> {
    // TODO: API call
    policyConfig.value = { ...policyConfig.value, ...config }
  }

  async function approveGate(gateId: string): Promise<void> {
    // TODO: API call
    const gate = approvalGates.value.find(g => g.gate_id === gateId)
    if (gate) {
      gate.status = 'approved'
    }
  }

  async function rejectGate(gateId: string): Promise<void> {
    // TODO: API call
    const gate = approvalGates.value.find(g => g.gate_id === gateId)
    if (gate) {
      gate.status = 'rejected'
    }
  }

  async function fetchDecisions(): Promise<void> {
    // TODO: API call
  }

  async function fetchAuditLog(): Promise<void> {
    // TODO: API call
  }

  return {
    policyConfig,
    decisions,
    approvalGates,
    auditLog,
    pendingGates,
    recentDecisions,
    approvalRate,
    fetchPolicyConfig,
    updatePolicyConfig,
    approveGate,
    rejectGate,
    fetchDecisions,
    fetchAuditLog
  }
})
