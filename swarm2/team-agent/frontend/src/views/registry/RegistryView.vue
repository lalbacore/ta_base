<template>
  <div class="registry-view">
    <div class="page-header">
      <div>
        <h1 class="page-title">Capability Registry</h1>
        <p class="page-subtitle">
          Browse and discover agent capabilities for your missions
        </p>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="summary-grid" v-if="statistics">
      <Card>
        <template #content>
          <div class="summary-card">
            <div class="summary-icon capabilities">
              <i class="pi pi-box"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Total Capabilities</div>
              <div class="summary-value">{{ statistics.total_capabilities }}</div>
            </div>
          </div>
        </template>
      </Card>

      <Card>
        <template #content>
          <div class="summary-card">
            <div class="summary-icon providers">
              <i class="pi pi-users"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Active Providers</div>
              <div class="summary-value">{{ statistics.total_providers }}</div>
            </div>
          </div>
        </template>
      </Card>

      <Card>
        <template #content>
          <div class="summary-card">
            <div class="summary-icon trust">
              <i class="pi pi-shield"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Avg Trust Score</div>
              <div class="summary-value">{{ statistics.average_trust_score }}</div>
            </div>
          </div>
        </template>
      </Card>

      <Card>
        <template #content>
          <div class="summary-card">
            <div class="summary-icon invocations">
              <i class="pi pi-chart-line"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Total Invocations</div>
              <div class="summary-value">{{ statistics.total_invocations }}</div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Filters -->
    <Card class="filters-card">
      <template #content>
        <div class="filters-container">
          <div class="filter-group">
            <label for="search">Search</label>
            <InputText
              id="search"
              v-model="searchTerm"
              placeholder="Search capabilities..."
              class="w-full"
            />
          </div>

          <div class="filter-group">
            <label for="type">Capability Type</label>
            <Dropdown
              id="type"
              v-model="selectedType"
              :options="capabilityTypes"
              placeholder="All Types"
              class="w-full"
              showClear
            />
          </div>

          <div class="filter-group">
            <label for="minTrust">Min Trust Score</label>
            <InputNumber
              id="minTrust"
              v-model="minTrustScore"
              :min="0"
              :max="100"
              placeholder="0"
              class="w-full"
            />
          </div>

          <div class="filter-group">
            <label for="maxPrice">Max Price</label>
            <InputNumber
              id="maxPrice"
              v-model="maxPrice"
              :min="0"
              placeholder="No limit"
              class="w-full"
              prefix="$"
            />
          </div>

          <div class="filter-actions">
            <Button
              label="Apply Filters"
              icon="pi pi-filter"
              @click="applyFilters"
            />
            <Button
              label="Clear"
              icon="pi pi-times"
              severity="secondary"
              text
              @click="clearFilters"
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <ProgressSpinner />
      <p>Loading capabilities...</p>
    </div>

    <!-- Capabilities Grid -->
    <div v-else-if="capabilities.length > 0" class="capabilities-section">
      <div class="section-header">
        <h2>Available Capabilities ({{ capabilities.length }})</h2>
      </div>
      <div class="capabilities-grid">
        <CapabilityCard
          v-for="cap in capabilities"
          :key="cap.capability_id"
          :capability="cap"
          @select="handleSelect"
          @view-details="handleViewDetails"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <i class="pi pi-box empty-icon"></i>
      <h3>No Capabilities Found</h3>
      <p>Try adjusting your filters or search terms</p>
      <Button
        label="Clear Filters"
        icon="pi pi-times"
        @click="clearFilters"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dropdown from 'primevue/dropdown'
import ProgressSpinner from 'primevue/progressspinner'
import { useRegistryStore } from '@/stores/registry.store'
import CapabilityCard from '@/components/registry/CapabilityCard.vue'
import type { Capability } from '@/types/registry.types'

const toast = useToast()
const registryStore = useRegistryStore()

const searchTerm = ref('')
const selectedType = ref('')
const minTrustScore = ref<number | null>(null)
const maxPrice = ref<number | null>(null)

const isLoading = computed(() => registryStore.isLoading)
const capabilities = computed(() => registryStore.capabilities)
const statistics = computed(() => registryStore.statistics)

const capabilityTypes = [
  'code_generation',
  'security_audit',
  'testing',
  'data_analysis',
  'deployment',
  'documentation',
  'code_review',
  'monitoring',
  'refactoring',
  'database_design',
  'performance_optimization',
  'cicd',
  'api_integration',
  'machine_learning'
]

async function applyFilters() {
  const filters: any = {}
  
  if (searchTerm.value) filters.search = searchTerm.value
  if (selectedType.value) filters.capability_type = selectedType.value
  if (minTrustScore.value !== null) filters.min_trust_score = minTrustScore.value
  if (maxPrice.value !== null) filters.max_price = maxPrice.value

  try {
    await registryStore.fetchCapabilities(filters)
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Filter Failed',
      detail: 'Failed to apply filters',
      life: 3000
    })
  }
}

async function clearFilters() {
  searchTerm.value = ''
  selectedType.value = ''
  minTrustScore.value = null
  maxPrice.value = null
  
  try {
    await registryStore.fetchCapabilities({})
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Load Failed',
      detail: 'Failed to load capabilities',
      life: 3000
    })
  }
}

function handleSelect(capability: Capability) {
  toast.add({
    severity: 'info',
    summary: 'Capability Selected',
    detail: `Selected: ${capability.name}`,
    life: 3000
  })
  console.log('Selected capability:', capability)
}

function handleViewDetails(capability: Capability) {
  console.log('View details:', capability)
  // TODO: Show detailed capability modal
}

onMounted(async () => {
  try {
    await Promise.all([
      registryStore.fetchCapabilities(),
      registryStore.fetchStatistics()
    ])
  } catch (error) {
    console.error('Failed to load registry data:', error)
    toast.add({
      severity: 'error',
      summary: 'Load Failed',
      detail: 'Failed to load registry data',
      life: 3000
    })
  }
})
</script>

<style scoped>
.registry-view {
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.summary-icon.capabilities {
  background: #dbeafe;
  color: #2563eb;
}

.summary-icon.providers {
  background: #d1fae5;
  color: #059669;
}

.summary-icon.trust {
  background: #fef3c7;
  color: #d97706;
}

.summary-icon.invocations {
  background: #e9d5ff;
  color: #9333ea;
}

.summary-content {
  flex: 1;
}

.summary-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.summary-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1e293b;
}

.filters-card {
  margin-bottom: 2rem;
}

.filters-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #1e293b;
  font-size: 0.875rem;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
}

.w-full {
  width: 100%;
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

.capabilities-section {
  margin-top: 2rem;
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
}

.capabilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
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
  margin-bottom: 1.5rem;
}
</style>
