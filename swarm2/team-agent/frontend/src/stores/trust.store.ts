import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TrustMetrics, TrustEvent, TrustHistory } from '@/types/trust.types'

export const useTrustStore = defineStore('trust', () => {
  // State
  const agents = ref<Map<string, TrustMetrics>>(new Map())
  const events = ref<Map<string, TrustEvent[]>>(new Map())
  const history = ref<Map<string, TrustHistory>>(new Map())
  const statistics = ref({
    total_agents: 0,
    average_trust_score: 0,
    total_operations: 0,
    total_incidents: 0
  })

  // Getters
  const sortedAgents = computed(() =>
    Array.from(agents.value.values()).sort((a, b) => b.trust_score - a.trust_score)
  )

  const topAgents = computed(() => sortedAgents.value.slice(0, 10))

  const lowTrustAgents = computed(() =>
    Array.from(agents.value.values()).filter(a => a.trust_score < 50)
  )

  // Actions
  async function fetchAllAgents(): Promise<void> {
    // TODO: API call
  }

  async function fetchAgentDetails(agentId: string): Promise<TrustMetrics | null> {
    // TODO: API call
    return agents.value.get(agentId) || null
  }

  async function fetchAgentHistory(agentId: string): Promise<TrustHistory | null> {
    // TODO: API call
    return history.value.get(agentId) || null
  }

  async function fetchAgentEvents(agentId: string): Promise<TrustEvent[]> {
    // TODO: API call
    return events.value.get(agentId) || []
  }

  return {
    agents,
    events,
    history,
    statistics,
    sortedAgents,
    topAgents,
    lowTrustAgents,
    fetchAllAgents,
    fetchAgentDetails,
    fetchAgentHistory,
    fetchAgentEvents
  }
})
