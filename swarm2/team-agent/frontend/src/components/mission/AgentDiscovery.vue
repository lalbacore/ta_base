<template>
  <div class="agent-discovery">
    <!-- Discovery Filters -->
    <Card class="filters-card">
      <template #title>
        <div class="filter-header">
          <span>Discover Agents</span>
          <Button
            icon="pi pi-refresh"
            size="small"
            text
            rounded
            @click="loadAgents"
            :loading="loading"
            v-tooltip.top="'Refresh agents'"
          />
        </div>
      </template>
      <template #content>
        <div class="filters-grid">
          <div class="filter-field">
            <label>Agent Type</label>
            <Dropdown
              v-model="filters.agent_type"
              :options="agentTypeOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="All types"
              showClear
              @change="loadAgents"
            />
          </div>

          <div class="filter-field">
            <label>Min Trust Score</label>
            <Slider
              v-model="filters.min_trust_score"
              :min="0"
              :max="100"
              :step="10"
              @slideend="loadAgents"
            />
            <small class="p-text-secondary">{{ filters.min_trust_score }}%</small>
          </div>

          <div class="filter-field">
            <label>Min Success Rate</label>
            <Slider
              v-model="filters.min_success_rate_pct"
              :min="0"
              :max="100"
              :step="10"
              @slideend="loadAgents"
            />
            <small class="p-text-secondary">{{ filters.min_success_rate_pct }}%</small>
          </div>
        </div>
      </template>
    </Card>

    <!-- Discovery Results -->
    <div v-if="loading" class="loading-state">
      <ProgressSpinner />
      <p>Discovering agents...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <Message severity="error" :closable="false">
        {{ error }}
      </Message>
    </div>

    <div v-else-if="agents.length === 0" class="empty-state">
      <Message severity="info" :closable="false">
        No agents found matching the criteria. Try adjusting the filters.
      </Message>
    </div>

    <div v-else class="agents-grid">
      <Card
        v-for="agent in agents"
        :key="agent.agent_id"
        class="agent-card"
        :class="{ 'selected': isSelected(agent.agent_id) }"
      >
        <template #header>
          <div class="agent-header">
            <div class="agent-info">
              <Tag
                :value="agent.agent_type"
                :severity="getAgentTypeSeverity(agent.agent_type)"
                class="agent-type-tag"
              />
              <h3>{{ agent.agent_name }}</h3>
            </div>
            <Checkbox
              v-model="selectedAgents"
              :value="agent.agent_id"
              @change="handleAgentSelection"
            />
          </div>
        </template>
        <template #content>
          <p class="agent-description">{{ agent.description }}</p>

          <!-- Trust Metrics -->
          <div class="metrics">
            <div class="metric">
              <label>Trust Score</label>
              <div class="metric-value">
                <ProgressBar
                  :value="agent.trust_score"
                  :showValue="false"
                  :class="getTrustScoreClass(agent.trust_score)"
                  class="trust-bar"
                />
                <span class="metric-number">{{ agent.trust_score.toFixed(1) }}</span>
              </div>
            </div>

            <div class="metric">
              <label>Success Rate</label>
              <div class="metric-value">
                <ProgressBar
                  :value="agent.success_rate * 100"
                  :showValue="false"
                  :class="getSuccessRateClass(agent.success_rate)"
                  class="success-bar"
                />
                <span class="metric-number">{{ (agent.success_rate * 100).toFixed(0) }}%</span>
              </div>
            </div>
          </div>

          <!-- Capabilities -->
          <div v-if="agent.capabilities.length > 0" class="capabilities">
            <label class="capabilities-label">Capabilities:</label>
            <div class="capability-tags">
              <Tag
                v-for="cap in agent.capabilities.slice(0, 3)"
                :key="cap.capability_id"
                :value="cap.capability_type"
                severity="secondary"
                class="capability-tag"
              />
              <Tag
                v-if="agent.capabilities.length > 3"
                :value="`+${agent.capabilities.length - 3} more`"
                severity="secondary"
                class="capability-tag"
              />
            </div>
          </div>

          <!-- Stats -->
          <div class="stats">
            <div class="stat">
              <i class="pi pi-chart-line"></i>
              <span>{{ agent.total_invocations }} invocations</span>
            </div>
            <div v-if="agent.average_rating > 0" class="stat">
              <i class="pi pi-star-fill"></i>
              <span>{{ agent.average_rating.toFixed(1) }}/5.0</span>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Selection Summary -->
    <div v-if="selectedAgents.length > 0" class="selection-summary">
      <Card>
        <template #content>
          <div class="summary-content">
            <div class="summary-info">
              <i class="pi pi-check-circle"></i>
              <span><strong>{{ selectedAgents.length }}</strong> agent{{ selectedAgents.length > 1 ? 's' : '' }} selected</span>
            </div>
            <Button
              label="Clear Selection"
              icon="pi pi-times"
              text
              size="small"
              @click="clearSelection"
            />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import Slider from 'primevue/slider'
import Checkbox from 'primevue/checkbox'
import Tag from 'primevue/tag'
import ProgressBar from 'primevue/progressbar'
import ProgressSpinner from 'primevue/progressspinner'
import Message from 'primevue/message'
import missionService from '@/services/mission.service'
import type { AgentCard } from '@/types/agent.types'

const props = defineProps<{
  modelValue: string[]  // Selected agent IDs
  minTrustScore?: number
  agentType?: 'role' | 'specialist' | 'tool'
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
  (e: 'agents-loaded', agents: AgentCard[]): void
}>()

const agents = ref<AgentCard[]>([])
const selectedAgents = ref<string[]>(props.modelValue || [])
const loading = ref(false)
const error = ref<string | null>(null)

const filters = ref({
  agent_type: props.agentType || null,
  min_trust_score: props.minTrustScore || 0,
  min_success_rate_pct: 0
})

const agentTypeOptions = [
  { label: 'All Types', value: null },
  { label: 'Role Agents', value: 'role' },
  { label: 'Specialists', value: 'specialist' },
  { label: 'Tools', value: 'tool' }
]

async function loadAgents() {
  loading.value = true
  error.value = null

  try {
    const response = await missionService.discoverAgents({
      agent_type: filters.value.agent_type || undefined,
      min_trust_score: filters.value.min_trust_score,
      min_success_rate: filters.value.min_success_rate_pct / 100
    })

    agents.value = response.agents
    emit('agents-loaded', response.agents)
  } catch (err) {
    error.value = 'Failed to discover agents. Please try again.'
    console.error('Agent discovery error:', err)
  } finally {
    loading.value = false
  }
}

function handleAgentSelection() {
  emit('update:modelValue', selectedAgents.value)
}

function isSelected(agentId: string): boolean {
  return selectedAgents.value.includes(agentId)
}

function clearSelection() {
  selectedAgents.value = []
  emit('update:modelValue', [])
}

function getAgentTypeSeverity(type: string) {
  switch (type) {
    case 'role': return 'info'
    case 'specialist': return 'success'
    case 'tool': return 'warning'
    default: return 'secondary'
  }
}

function getTrustScoreClass(score: number): string {
  if (score >= 90) return 'trust-high'
  if (score >= 75) return 'trust-medium'
  return 'trust-low'
}

function getSuccessRateClass(rate: number): string {
  if (rate >= 0.95) return 'success-high'
  if (rate >= 0.80) return 'success-medium'
  return 'success-low'
}

onMounted(() => {
  loadAgents()
})
</script>

<style scoped>
.agent-discovery {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.filters-card {
  background-color: #f8fafc;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-field label {
  font-weight: 600;
  font-size: 0.875rem;
  color: #334155;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1rem;
}

.agent-card {
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.agent-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.agent-card.selected {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.agent-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.agent-info h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.agent-type-tag {
  align-self: flex-start;
}

.agent-description {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.metrics {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
}

.metric-value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.metric-value :deep(.p-progressbar) {
  flex: 1;
  height: 8px;
}

.metric-number {
  min-width: 40px;
  text-align: right;
  font-weight: 600;
  font-size: 0.875rem;
}

:deep(.trust-high .p-progressbar-value) {
  background: #10b981;
}

:deep(.trust-medium .p-progressbar-value) {
  background: #f59e0b;
}

:deep(.trust-low .p-progressbar-value) {
  background: #ef4444;
}

:deep(.success-high .p-progressbar-value) {
  background: #10b981;
}

:deep(.success-medium .p-progressbar-value) {
  background: #f59e0b;
}

:deep(.success-low .p-progressbar-value) {
  background: #ef4444;
}

.capabilities {
  margin-bottom: 1rem;
}

.capabilities-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  display: block;
  margin-bottom: 0.5rem;
}

.capability-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.capability-tag {
  font-size: 0.75rem;
}

.stats {
  display: flex;
  gap: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: #64748b;
}

.stat i {
  color: #94a3b8;
}

.selection-summary {
  position: sticky;
  bottom: 1rem;
  z-index: 10;
}

.selection-summary :deep(.p-card) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.summary-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1rem;
}

.summary-info i {
  font-size: 1.5rem;
  color: #10b981;
}

.p-text-secondary {
  color: #64748b;
  font-size: 0.875rem;
}
</style>
