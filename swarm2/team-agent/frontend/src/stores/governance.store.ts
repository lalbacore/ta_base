import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PolicyConfig, GovernanceDecision } from '@/types/governance.types'

export const useGovernanceStore = defineStore('governance', () => {
  const policyConfig = ref<PolicyConfig | null>(null)
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

  return {
    policyConfig,
    decisions,
    isLoading,
    fetchPolicyConfig,
    updatePolicyConfig,
    fetchDecisions
  }
})
