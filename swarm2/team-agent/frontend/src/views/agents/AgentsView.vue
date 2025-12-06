<template>
  <div class="agents-view">
    <div class="page-header">
      <div>
        <h1 class="page-title">Agent Manager</h1>
        <p class="page-subtitle">
          Discover and monitor workflow agents and their performance metrics
        </p>
      </div>
    </div>

    <!-- Summary Metrics -->
    <div class="metrics-grid" v-if="systemStats">
      <div class="metric-card">
        <div class="metric-icon" style="background-color: #3b82f6;">
          <i class="pi pi-users"></i>
        </div>
        <div class="metric-content">
          <div class="metric-value">{{ systemStats.total_agents }}</div>
          <div class="metric-label">Total Agents</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon" style="background-color: #10b981;">
          <i class="pi pi-bolt"></i>
        </div>
        <div class="metric-content">
          <div class="metric-value">{{ systemStats.total_invocations }}</div>
          <div class="metric-label">Total Invocations</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon" style="background-color: #8b5cf6;">
          <i class="pi pi-shield"></i>
        </div>
        <div class="metric-content">
          <div class="metric-value">{{ systemStats.average_trust_score.toFixed(1) }}</div>
          <div class="metric-label">Avg Trust Score</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon" style="background-color: #f59e0b;">
          <i class="pi pi-star-fill"></i>
        </div>
        <div class="metric-content">
          <div class="metric-value">{{ systemStats.top_agents.length }}</div>
          <div class="metric-label">Top Performers</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <label>Agent Type</label>
        <Dropdown
          v-model="filters.type"
          :options="typeOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="All Types"
          :showClear="true"
          @change="fetchAgents"
        />
      </div>

      <div class="filter-group">
        <label>Trust Domain</label>
        <Dropdown
          v-model="filters.domain"
          :options="domainOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="All Domains"
          :showClear="true"
          @change="fetchAgents"
        />
      </div>

      <div class="filter-group">
        <label>Status</label>
        <Dropdown
          v-model="filters.status"
          :options="statusOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="All Statuses"
          :showClear="true"
          @change="fetchAgents"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <ProgressSpinner />
      <p>Loading agents...</p>
    </div>

    <!-- Agents List -->
    <div v-else-if="agents.length > 0" class="agents-container">
      <DataTable
        :value="agents"
        :paginator="true"
        :rows="10"
        :rowsPerPageOptions="[10, 25, 50]"
        responsiveLayout="scroll"
        @row-click="handleRowClick"
        class="agents-table"
      >
        <Column field="agent_name" header="Agent Name" :sortable="true">
          <template #body="slotProps">
            <div class="agent-name-cell">
              <i class="pi pi-circle-fill" :style="{ color: getStatusColor(slotProps.data.status) }"></i>
              <strong>{{ slotProps.data.agent_name }}</strong>
            </div>
          </template>
        </Column>

        <Column field="agent_type" header="Type" :sortable="true">
          <template #body="slotProps">
            <Tag :value="slotProps.data.agent_type" severity="info" />
          </template>
        </Column>

        <Column field="trust_domain" header="Trust Domain" :sortable="true">
          <template #body="slotProps">
            <Tag :value="slotProps.data.trust_domain" :severity="getDomainSeverity(slotProps.data.trust_domain)" />
          </template>
        </Column>

        <Column field="trust_score" header="Trust Score" :sortable="true">
          <template #body="slotProps">
            <div class="trust-score-cell">
              <ProgressBar
                :value="slotProps.data.trust_score"
                :showValue="false"
                :style="{ height: '8px', width: '100px' }"
              />
              <span class="trust-score-value">{{ slotProps.data.trust_score.toFixed(1) }}</span>
            </div>
          </template>
        </Column>

        <Column field="total_invocations" header="Invocations" :sortable="true">
          <template #body="slotProps">
            <span class="invocations-count">{{ slotProps.data.total_invocations }}</span>
          </template>
        </Column>

        <Column field="success_rate" header="Success Rate" :sortable="true">
          <template #body="slotProps">
            <span :class="getSuccessRateClass(slotProps.data.success_rate)">
              {{ (slotProps.data.success_rate * 100).toFixed(1) }}%
            </span>
          </template>
        </Column>

        <Column field="status" header="Status" :sortable="true">
          <template #body="slotProps">
            <Tag
              :value="slotProps.data.status"
              :severity="slotProps.data.status === 'active' ? 'success' : 'danger'"
            />
          </template>
        </Column>

        <Column header="Actions">
          <template #body="slotProps">
            <Button
              icon="pi pi-eye"
              text
              rounded
              @click.stop="viewAgentDetails(slotProps.data)"
              v-tooltip.top="'View Details'"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <i class="pi pi-users empty-icon"></i>
      <h3>No Agents Found</h3>
      <p>Agents will appear here once they are registered and start executing workflows</p>
    </div>

    <!-- Agent Detail Dialog -->
    <Dialog
      v-model:visible="showDetailDialog"
      :header="selectedAgent?.agent_name"
      :modal="true"
      :style="{ width: '800px' }"
    >
      <div v-if="selectedAgent" class="agent-detail">
        <div class="detail-section">
          <h4>Overview</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <label>Agent ID:</label>
              <span>{{ selectedAgent.agent_id }}</span>
            </div>
            <div class="detail-item">
              <label>Type:</label>
              <Tag :value="selectedAgent.agent_type" severity="info" />
            </div>
            <div class="detail-item">
              <label>Trust Domain:</label>
              <Tag :value="selectedAgent.trust_domain" :severity="getDomainSeverity(selectedAgent.trust_domain)" />
            </div>
            <div class="detail-item">
              <label>Version:</label>
              <span>{{ selectedAgent.version }}</span>
            </div>
          </div>
          <div class="detail-item full-width">
            <label>Description:</label>
            <p>{{ selectedAgent.description }}</p>
          </div>
        </div>

        <div class="detail-section" v-if="agentStats">
          <h4>Performance Metrics</h4>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ agentStats.total_invocations }}</div>
              <div class="stat-label">Total Invocations</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ agentStats.successful_invocations }}</div>
              <div class="stat-label">Successful</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ agentStats.failed_invocations }}</div>
              <div class="stat-label">Failed</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ (agentStats.average_duration / 1000).toFixed(2) }}s</div>
              <div class="stat-label">Avg Duration</div>
            </div>
          </div>
        </div>

        <div class="detail-section" v-if="recentInvocations.length > 0">
          <h4>Recent Invocations</h4>
          <DataTable :value="recentInvocations" :paginator="false" responsiveLayout="scroll">
            <Column field="workflow_id" header="Workflow ID">
              <template #body="slotProps">
                <code class="workflow-id">{{ slotProps.data.workflow_id }}</code>
              </template>
            </Column>
            <Column field="status" header="Status">
              <template #body="slotProps">
                <Tag
                  :value="slotProps.data.status"
                  :severity="slotProps.data.status === 'success' ? 'success' : 'danger'"
                />
              </template>
            </Column>
            <Column field="duration" header="Duration">
              <template #body="slotProps">
                {{ (slotProps.data.duration / 1000).toFixed(2) }}s
              </template>
            </Column>
            <Column field="started_at" header="Started At">
              <template #body="slotProps">
                {{ formatDate(slotProps.data.started_at) }}
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Dropdown from 'primevue/dropdown'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import ProgressSpinner from 'primevue/progressspinner'
import Dialog from 'primevue/dialog'
import agentsService from '@/services/agents.service'
import type { AgentCard, AgentInvocation, AgentStats, SystemStatsResponse } from '@/types/agents.types'

const router = useRouter()

const isLoading = ref(false)
const agents = ref<AgentCard[]>([])
const systemStats = ref<SystemStatsResponse | null>(null)
const showDetailDialog = ref(false)
const selectedAgent = ref<AgentCard | null>(null)
const agentStats = ref<AgentStats | null>(null)
const recentInvocations = ref<AgentInvocation[]>([])

const filters = ref({
  type: null as string | null,
  domain: null as string | null,
  status: null as string | null
})

const typeOptions = [
  { label: 'Role', value: 'role' },
  { label: 'Specialist', value: 'specialist' },
  { label: 'Capability', value: 'capability' }
]

const domainOptions = [
  { label: 'Execution', value: 'EXECUTION' },
  { label: 'Government', value: 'GOVERNMENT' },
  { label: 'Logging', value: 'LOGGING' }
]

const statusOptions = [
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' }
]

async function fetchAgents() {
  isLoading.value = true
  try {
    const response = await agentsService.listAgents({
      type: filters.value.type || undefined,
      domain: filters.value.domain || undefined,
      status: filters.value.status || undefined
    })
    agents.value = response.agents
  } catch (error) {
    console.error('Failed to fetch agents:', error)
  } finally {
    isLoading.value = false
  }
}

async function fetchSystemStats() {
  try {
    systemStats.value = await agentsService.getSystemStats()
  } catch (error) {
    console.error('Failed to fetch system stats:', error)
  }
}

async function viewAgentDetails(agent: AgentCard) {
  selectedAgent.value = agent
  showDetailDialog.value = true

  try {
    const detail = await agentsService.getAgent(agent.agent_id)
    agentStats.value = detail.stats
    recentInvocations.value = detail.recent_invocations
  } catch (error) {
    console.error('Failed to fetch agent details:', error)
  }
}

function handleRowClick(event: any) {
  viewAgentDetails(event.data)
}

function getStatusColor(status: string): string {
  return status === 'active' ? '#10b981' : '#ef4444'
}

function getDomainSeverity(domain: string): string {
  const severities: Record<string, string> = {
    'EXECUTION': 'info',
    'GOVERNMENT': 'warning',
    'LOGGING': 'success'
  }
  return severities[domain] || 'info'
}

function getSuccessRateClass(rate: number): string {
  if (rate >= 0.9) return 'success-rate-high'
  if (rate >= 0.7) return 'success-rate-medium'
  return 'success-rate-low'
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

onMounted(async () => {
  await Promise.all([
    fetchAgents(),
    fetchSystemStats()
  ])
})
</script>

<style scoped>
.agents-view {
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

.metric-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  color: white;
  font-size: 1.5rem;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.metric-label {
  font-size: 0.875rem;
  color: #64748b;
}

.filters-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
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

.agents-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.agent-name-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.agent-name-cell i {
  font-size: 0.5rem;
}

.trust-score-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.trust-score-value {
  font-weight: 600;
  color: #1e293b;
}

.invocations-count {
  font-weight: 600;
  color: #3b82f6;
}

.success-rate-high {
  color: #10b981;
  font-weight: 600;
}

.success-rate-medium {
  color: #f59e0b;
  font-weight: 600;
}

.success-rate-low {
  color: #ef4444;
  font-weight: 600;
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

.agent-detail {
  padding: 1rem 0;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
}

.detail-item span, .detail-item p {
  color: #1e293b;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
}

.workflow-id {
  font-family: monospace;
  font-size: 0.875rem;
  background: #f1f5f9;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}
</style>
