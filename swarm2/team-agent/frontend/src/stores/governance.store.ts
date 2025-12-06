import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Policy, PolicyConfig, GovernanceDecision } from '@/types/governance.types'

export const useGovernanceStore = defineStore('governance', () => {
  const policyConfig = ref<PolicyConfig | null>(null)
  const policies = ref<Policy[]>([])
  const decisions = ref<GovernanceDecision[]>([])
  const isLoading = ref(false)

  async function fetchPolicyConfig(): Promise<void> {
    const governanceService = await import('@/services/governance.service')
    isLoading.value = true
    try {
      policyConfig.value = await governanceService.default.getPolicyConfig()
    } finally {
      isLoading.value = false
    }
  }

  async function updatePolicyConfig(config: PolicyConfig): Promise<void> {
    const governanceService = await import('@/services/governance.service')
    await governanceService.default.updatePolicyConfig(config)
    policyConfig.value = config
  }

  async function fetchDecisions(limit: number = 50): Promise<void> {
    const governanceService = await import('@/services/governance.service')
    decisions.value = await governanceService.default.getDecisions(limit)
  }

  // Policy Management Methods

  async function fetchPolicies(): Promise<void> {
    const governanceService = await import('@/services/governance.service')
    isLoading.value = true
    try {
      policies.value = await governanceService.default.getAllPolicies()
    } finally {
      isLoading.value = false
    }
  }

  async function createPolicy(policyData: Omit<Policy, 'id' | 'created_at' | 'updated_at' | 'is_active'>): Promise<Policy> {
    const governanceService = await import('@/services/governance.service')
    const newPolicy = await governanceService.default.createPolicy(policyData)
    policies.value.push(newPolicy)
    return newPolicy
  }

  async function updatePolicy(policyId: number, policyData: Partial<Policy>): Promise<Policy> {
    const governanceService = await import('@/services/governance.service')
    const updatedPolicy = await governanceService.default.updatePolicy(policyId, policyData)
    const index = policies.value.findIndex(p => p.id === policyId)
    if (index !== -1) {
      policies.value[index] = updatedPolicy
    }
    return updatedPolicy
  }

  async function deletePolicy(policyId: number): Promise<void> {
    const governanceService = await import('@/services/governance.service')
    await governanceService.default.deletePolicy(policyId)
    policies.value = policies.value.filter(p => p.id !== policyId)
  }

  async function activatePolicy(policyId: number): Promise<Policy> {
    const governanceService = await import('@/services/governance.service')
    const activatedPolicy = await governanceService.default.activatePolicy(policyId)

    // Deactivate all policies and activate the selected one
    policies.value = policies.value.map(p => ({
      ...p,
      is_active: p.id === policyId
    }))

    // Refresh policy config to show the new active policy
    await fetchPolicyConfig()

    return activatedPolicy
  }

  return {
    policyConfig,
    policies,
    decisions,
    isLoading,
    fetchPolicyConfig,
    updatePolicyConfig,
    fetchDecisions,
    fetchPolicies,
    createPolicy,
    updatePolicy,
    deletePolicy,
    activatePolicy
  }
})
