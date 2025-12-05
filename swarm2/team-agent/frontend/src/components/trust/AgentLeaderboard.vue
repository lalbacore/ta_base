<template>
  <div class="agent-leaderboard">
    <div class="leaderboard-header">
      <h2>Agent Trust Leaderboard</h2>
      <div class="sort-controls">
        <label>Sort by:</label>
        <Dropdown
          v-model="sortBy"
          :options="sortOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Sort by..."
        />
      </div>
    </div>

    <DataTable
      :value="sortedAgents"
      :paginator="true"
      :rows="10"
      :rowsPerPageOptions="[5, 10, 20]"
      class="p-datatable-sm"
      stripedRows
      @row-click="handleRowClick"
    >
      <Column field="name" header="Agent Name" :sortable="true">
        <template #body="slotProps">
          <div class="agent-name-cell">
            <i :class="getAgentIcon(slotProps.data.type)"></i>
            <span class="agent-name">{{ slotProps.data.name }}</span>
          </div>
        </template>
      </Column>

      <Column field="type" header="Type" :sortable="true">
        <template #body="slotProps">
          <Tag :severity="getTypeSeverity(slotProps.data.type)">
            {{ formatType(slotProps.data.type) }}
          </Tag>
        </template>
      </Column>

      <Column field="trust_score" header="Trust Score" :sortable="true">
        <template #body="slotProps">
          <div class="trust-score-cell">
            <ProgressBar
              :value="slotProps.data.trust_score"
              :showValue="false"
              :class="getTrustScoreClass(slotProps.data.trust_score)"
            />
            <span class="score-value">{{ slotProps.data.trust_score }}</span>
          </div>
        </template>
      </Column>

      <Column field="reputation" header="Reputation" :sortable="true">
        <template #body="slotProps">
          <div class="reputation-cell">
            <i class="pi pi-star-fill" style="color: #fbbf24"></i>
            <span>{{ slotProps.data.reputation.toFixed(1) }}</span>
          </div>
        </template>
      </Column>

      <Column field="total_operations" header="Operations" :sortable="true">
        <template #body="slotProps">
          <span class="operations-count">{{ slotProps.data.total_operations }}</span>
        </template>
      </Column>

      <Column field="success_rate" header="Success Rate" :sortable="true">
        <template #body="slotProps">
          <Tag :severity="getSuccessSeverity(slotProps.data.success_rate)">
            {{ (slotProps.data.success_rate * 100).toFixed(0) }}%
          </Tag>
        </template>
      </Column>

      <Column field="last_active" header="Last Active" :sortable="true">
        <template #body="slotProps">
          <span class="last-active">{{ formatLastActive(slotProps.data.last_active) }}</span>
        </template>
      </Column>

      <Column header="Actions">
        <template #body="slotProps">
          <Button
            icon="pi pi-eye"
            text
            rounded
            size="small"
            @click.stop="viewDetails(slotProps.data)"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import ProgressBar from 'primevue/progressbar'
import Dropdown from 'primevue/dropdown'

interface Agent {
  agent_id: string
  name: string
  type: string
  trust_score: number
  reputation: number
  total_operations: number
  success_rate: number
  security_incidents: number
  policy_violations: number
  last_active: string
}

interface Props {
  agents: Agent[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'view-details', agent: Agent): void
  (e: 'row-click', event: any): void
}>()

const sortBy = ref('trust_score')
const sortOptions = [
  { label: 'Trust Score', value: 'trust_score' },
  { label: 'Reputation', value: 'reputation' },
  { label: 'Success Rate', value: 'success_rate' },
  { label: 'Total Operations', value: 'total_operations' },
  { label: 'Last Active', value: 'last_active' }
]

const sortedAgents = computed(() => {
  const agents = [...props.agents]
  return agents.sort((a, b) => {
    const aVal = a[sortBy.value as keyof Agent]
    const bVal = b[sortBy.value as keyof Agent]

    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return bVal - aVal // Descending
    }
    return 0
  })
})

function getAgentIcon(type: string): string {
  const iconMap: Record<string, string> = {
    code_generation: 'pi pi-code',
    security_audit: 'pi pi-shield',
    testing: 'pi pi-check-circle',
    data_analysis: 'pi pi-chart-bar',
    deployment: 'pi pi-cloud-upload',
    code_review: 'pi pi-eye'
  }
  return iconMap[type] || 'pi pi-cog'
}

function getTypeSeverity(type: string): string {
  const severityMap: Record<string, string> = {
    code_generation: 'info',
    security_audit: 'danger',
    testing: 'success',
    data_analysis: 'warning',
    deployment: 'secondary',
    code_review: 'info'
  }
  return severityMap[type] || 'secondary'
}

function formatType(type: string): string {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function getTrustScoreClass(score: number): string {
  if (score >= 90) return 'trust-excellent'
  if (score >= 75) return 'trust-good'
  if (score >= 60) return 'trust-fair'
  return 'trust-poor'
}

function getSuccessSeverity(rate: number): string {
  if (rate >= 0.9) return 'success'
  if (rate >= 0.75) return 'info'
  if (rate >= 0.6) return 'warning'
  return 'danger'
}

function formatLastActive(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${diffDays}d ago`
}

function handleRowClick(event: any) {
  emit('row-click', event)
}

function viewDetails(agent: Agent) {
  emit('view-details', agent)
}
</script>

<style scoped>
.agent-leaderboard {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.leaderboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.leaderboard-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-controls label {
  font-size: 0.875rem;
  color: #64748b;
}

.agent-name-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.agent-name-cell i {
  color: #64748b;
}

.agent-name {
  font-weight: 500;
}

.trust-score-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.trust-score-cell :deep(.p-progressbar) {
  flex: 1;
  height: 8px;
}

.score-value {
  font-weight: 600;
  min-width: 2rem;
  text-align: right;
}

.trust-excellent :deep(.p-progressbar-value) {
  background: #10b981;
}

.trust-good :deep(.p-progressbar-value) {
  background: #3b82f6;
}

.trust-fair :deep(.p-progressbar-value) {
  background: #f59e0b;
}

.trust-poor :deep(.p-progressbar-value) {
  background: #ef4444;
}

.reputation-cell {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.operations-count {
  font-weight: 500;
  color: #64748b;
}

.last-active {
  font-size: 0.875rem;
  color: #64748b;
}

:deep(.p-datatable .p-datatable-tbody > tr) {
  cursor: pointer;
  transition: background-color 0.2s;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: #f8fafc;
}
</style>
