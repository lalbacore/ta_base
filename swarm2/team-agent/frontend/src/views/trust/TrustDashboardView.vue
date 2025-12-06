<template>
  <div class="trust-dashboard">
    <div class="page-header">
      <div>
        <h1 class="page-title">Trust Scoring Dashboard</h1>
        <p class="page-subtitle">
          Monitor agent performance, trust scores, and reputation metrics
        </p>
      </div>
    </div>

    <!-- Summary Metrics -->
    <div class="metrics-grid">
      <TrustMetricsCard
        label="Total Agents"
        :value="agents.length"
        icon="pi pi-users"
        color="blue"
      />
      <TrustMetricsCard
        label="Average Trust Score"
        :value="averageTrustScore"
        icon="pi pi-shield"
        color="green"
        format="decimal"
      />
      <TrustMetricsCard
        label="High Trust Agents"
        :value="highTrustCount"
        icon="pi pi-star-fill"
        color="purple"
        :subtitle="`Score ≥ 90`"
      />
      <TrustMetricsCard
        label="Security Incidents"
        :value="totalSecurityIncidents"
        icon="pi pi-exclamation-triangle"
        color="red"
      />
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <ProgressSpinner />
      <p>Loading trust data...</p>
    </div>

    <!-- Agent Leaderboard -->
    <div v-else-if="agents.length > 0" class="leaderboard-container">
      <AgentLeaderboard
        :agents="agents"
        @view-details="handleViewDetails"
        @row-click="handleRowClick"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <i class="pi pi-shield empty-icon"></i>
      <h3>No Agents Available</h3>
      <p>Trust scores will appear here once agents start executing workflows</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ProgressSpinner from 'primevue/progressspinner'
import { useTrustStore } from '@/stores/trust.store'
import AgentLeaderboard from '@/components/trust/AgentLeaderboard.vue'
import TrustMetricsCard from '@/components/trust/TrustMetricsCard.vue'

const router = useRouter()
const trustStore = useTrustStore()

const isLoading = ref(false)

const agents = computed(() => Array.from(trustStore.agents.values()))

const averageTrustScore = computed(() => {
  if (agents.value.length === 0) return 0
  const sum = agents.value.reduce((acc, agent) => acc + agent.trust_score, 0)
  return sum / agents.value.length
})

const highTrustCount = computed(() => {
  return agents.value.filter(agent => agent.trust_score >= 90).length
})

const totalSecurityIncidents = computed(() => {
  return agents.value.reduce((acc, agent) => acc + agent.security_incidents, 0)
})

function handleViewDetails(agent: any) {
  // TODO: Navigate to agent detail view or show modal
  console.log('View details for:', agent)
}

function handleRowClick(event: any) {
  console.log('Row clicked:', event.data)
  // TODO: Navigate to agent detail page
  // router.push(`/trust/agent/${event.data.agent_id}`)
}

onMounted(async () => {
  isLoading.value = true
  try {
    await trustStore.fetchAllAgents()
  } catch (error) {
    console.error('Failed to load trust data:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.trust-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #1e293b;
}

.page-subtitle {
  color: #64748b;
  margin: 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6rem 0;
  color: #64748b;
}

.loading-state p {
  margin-top: 1rem;
}

.leaderboard-container {
  margin-top: 2rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  background-color: #f8fafc;
  margin-top: 2rem;
}

.empty-icon {
  font-size: 4rem;
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #94a3b8;
}
</style>
