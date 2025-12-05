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
    const trustService = await import('@/services/trust.service')
    const agentList = await trustService.default.getAllAgents()

    agentList.forEach(agent => {
      agents.value.set(agent.agent_id, agent)
    })

    // Update statistics
    statistics.value.total_agents = agentList.length
    statistics.value.average_trust_score = agentList.reduce((acc, a) => acc + a.trust_score, 0) / agentList.length
    statistics.value.total_operations = agentList.reduce((acc, a) => acc + a.total_operations, 0)
    statistics.value.total_incidents = agentList.reduce((acc, a) => acc + a.security_incidents, 0)
  }

  async function fetchAgentDetails(agentId: string): Promise<TrustMetrics | null> {
    const trustService = await import('@/services/trust.service')
    const agent = await trustService.default.getAgentDetails(agentId)

    if (agent) {
      agents.value.set(agentId, agent)
      return agent
    }

    return agents.value.get(agentId) || null
  }

  async function fetchAgentHistory(agentId: string): Promise<TrustHistory | null> {
    const trustService = await import('@/services/trust.service')
    const agentHistory = await trustService.default.getAgentHistory(agentId)

    if (agentHistory) {
      history.value.set(agentId, agentHistory)
      return agentHistory
    }

    return history.value.get(agentId) || null
  }

  async function fetchAgentEvents(agentId: string): Promise<TrustEvent[]> {
    const trustService = await import('@/services/trust.service')
    const agentEvents = await trustService.default.getAgentEvents(agentId)

    events.value.set(agentId, agentEvents)
    return agentEvents
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
