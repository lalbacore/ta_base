<template>
  
    <div class="mission-detail">
      <!-- Header -->
      <div class="page-header">
        <div>
          <Button
            label="Back to Missions"
            icon="pi pi-arrow-left"
            text
            size="small"
            @click="handleBack"
            class="back-button"
          />
          <div class="title-row">
            <h1 class="page-title">{{ missionId }}</h1>
            <Tag v-if="workflow" :severity="statusSeverity" class="status-tag">
              {{ workflow.status }}
            </Tag>
          </div>
          <p v-if="mission" class="mission-description">
            {{ mission.description }}
          </p>
        </div>

        <div class="header-actions">
           <div class="control-toolbar">
              <Button 
                v-if="workflow?.status === 'running'"
                icon="pi pi-pause" 
                label="Pause" 
                severity="warning" 
                @click="handlePause"
              />
              <Button 
                v-if="workflow?.status === 'paused'"
                icon="pi pi-play" 
                label="Resume" 
                severity="success" 
                @click="handleResume"
              />
              <Button 
                v-if="['running', 'paused'].includes(workflow?.status || '')"
                icon="pi pi-stop" 
                label="Cancel" 
                severity="danger" 
                outlined
                @click="handleCancel"
              />
           </div>
           
           <Menu ref="menu" :model="actionMenuItems" :popup="true" />
           <Button
             label="More"
             icon="pi pi-ellipsis-v"
             text
             plain
             @click="(event) => menu?.toggle(event)"
           />
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <ProgressSpinner />
        <p>Loading mission details...</p>
      </div>

      <!-- Error State -->
      <Message v-else-if="error" severity="error" :closable="false">
        {{ error }}
      </Message>

      <!-- Content -->
      <div v-else class="detail-grid">
        <!-- Main Content -->
        <div class="main-content">
          <!-- Progress Overview -->
          <Card>
            <template #content>
              <h3 class="section-title">Progress Overview</h3>

              <div class="progress-header">
                <span class="progress-label">Overall Progress</span>
                <span class="progress-value" :style="{ color: progressColor }">
                  {{ workflow?.progress || 0 }}%
                </span>
              </div>

              <ProgressBar
                :value="workflow?.progress || 0"
                :showValue="false"
                class="progress-bar"
              />

              <p class="current-stage">
                Current Stage: {{ formatStageName(workflow?.current_stage || 'none') }}
              </p>
            </template>
          </Card>

          <!-- Workflow Timeline -->
          <Card>
            <template #content>
              <div class="timeline-header-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                 <h3 class="section-title" style="margin-bottom: 0;">Workflow Timeline</h3>
                 <div class="debug-toggle" style="display: flex; align-items: center; gap: 0.5rem;">
                   <label for="debug-mode" style="font-size: 0.875rem; color: #64748b;">Debug Mode</label>
                   <InputSwitch inputId="debug-mode" v-model="debugMode" />
                 </div>
              </div>
              <WorkflowStageTimeline 
                :stages="workflow?.stages || []" 
                :debug-mode="debugMode"
              />
            </template>
          </Card>

          <!-- Pending Breakpoints -->
          <Message
            v-if="pendingBreakpoints.length > 0"
            severity="warn"
            :closable="false"
          >
            <h4>Approval Required</h4>
            <p>This workflow requires your approval to continue</p>
            <Button
              label="Review & Approve"
              severity="warning"
              @click="handleBreakpointApproval"
              class="mt-3"
            />
          </Message>
        </div>

        <!-- Sidebar -->
        <div class="sidebar-content">
          <!-- Mission Details Card -->
          <Card>
            <template #content>
              <h4 class="card-title">Mission Details</h4>

              <div class="detail-list">
                <div class="detail-item">
                  <span class="detail-label">Created</span>
                  <span class="detail-value">
                    {{ formatDate(workflow?.created_at) }}
                  </span>
                </div>

                <div class="detail-item">
                  <span class="detail-label">Last Updated</span>
                  <span class="detail-value">
                    {{ formatDate(workflow?.updated_at) }}
                  </span>
                </div>

                <Divider />

                <div class="detail-item">
                  <span class="detail-label">Min Trust Score</span>
                  <span class="detail-value detail-value-bold">
                    {{ mission?.min_trust_score || 0 }}
                  </span>
                </div>

                <div v-if="mission?.max_cost" class="detail-item">
                  <span class="detail-label">Max Cost</span>
                  <span class="detail-value detail-value-bold">
                    {{ mission.max_cost }} Tokens
                  </span>
                </div>
              </div>
            </template>
          </Card>

          <!-- Required Capabilities -->
          <Card v-if="mission?.required_capabilities && mission.required_capabilities.length > 0">
            <template #content>
              <h4 class="card-title">Required Capabilities</h4>

              <div class="capability-list">
                <Tag
                  v-for="(cap, index) in mission.required_capabilities"
                  :key="index"
                  severity="info"
                  class="capability-tag"
                >
                  {{ formatCapabilityType(cap.capability_type) }}
                </Tag>
              </div>
            </template>
          </Card>

          <!-- Breakpoints -->
          <Card v-if="mission?.breakpoints && mission.breakpoints.length > 0">
            <template #content>
              <h4 class="card-title">Breakpoints</h4>

              <ul class="breakpoint-list">
                <li
                  v-for="(bp, index) in mission.breakpoints"
                  :key="index"
                >
                  {{ formatBreakpointType(bp) }}
                </li>
              </ul>
            </template>
          </Card>
        </div>
      </div>

      <!-- Breakpoint Approval Modal -->
      <BreakpointApprovalModal
        :is-open="showBreakpointModal"
        :breakpoint="currentBreakpoint"
        @close="showBreakpointModal = false"
        @approved="handleBreakpointApproved"
        @rejected="handleBreakpointRejected"
      />
    </div>
  
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import ProgressBar from 'primevue/progressbar'
import ProgressSpinner from 'primevue/progressspinner'
import Message from 'primevue/message'
import Divider from 'primevue/divider'
import Menu from 'primevue/menu'
import { useMissionStore } from '@/stores/mission.store'
import { useWorkflowWebSocket } from '@/composables/useWorkflowWebSocket'
import WorkflowStageTimeline from '@/components/mission/WorkflowStageTimeline.vue'
import BreakpointApprovalModal from '@/components/mission/BreakpointApprovalModal.vue'

import InputSwitch from 'primevue/inputswitch'

const route = useRoute()
const router = useRouter()
const missionStore = useMissionStore()

const menu = ref()
const missionId = computed(() => route.params.id as string)
const mission = computed(() => missionStore.missions.get(missionId.value))
const workflow = computed(() => missionStore.workflows.get(missionId.value))

const isLoading = ref(false)
const error = ref('')
const refreshInterval = ref<number | null>(null)
const showBreakpointModal = ref(false)
const currentBreakpoint = ref<any>(null)
const debugMode = ref(false)

// Connect to WebSocket for real-time updates
const { isConnected } = useWorkflowWebSocket(missionId.value)

const pendingBreakpoints = computed(() =>
  Array.from(missionStore.breakpoints.values()).filter(
    bp => bp.workflow_id === missionId.value && bp.status === 'pending'
  )
)

const statusSeverity = computed(() => {
  switch (workflow.value?.status) {
    case 'running':
      return 'info'
    case 'completed':
      return 'success'
    case 'failed':
      return 'danger'
    case 'paused':
      return 'warning'
    default:
      return 'secondary'
  }
})

const progressColor = computed(() => {
  const progress = workflow.value?.progress || 0
  if (progress === 100) return '#10b981'
  if (progress >= 50) return '#3b82f6'
  return '#64748b'
})

const actionMenuItems = computed(() => [
  {
    label: 'Refresh Status',
    icon: 'pi pi-refresh',
    command: handleRefresh
  },
  ...(workflow.value?.status === 'paused' ? [{
    label: 'Resume Workflow',
    icon: 'pi pi-play',
    command: handleResume
  }] : []),
  { separator: true },
  {
    label: 'Cancel Mission',
    icon: 'pi pi-times',
    command: handleCancel,
    class: 'text-red-500'
  }
])

async function loadMissionDetails() {
  isLoading.value = true
  error.value = ''

  try {
    await missionStore.fetchWorkflowStatus(missionId.value)
  } catch (err) {
    error.value = 'Failed to load mission details'
    console.error('Error loading mission:', err)
  } finally {
    isLoading.value = false
  }
}

function formatStageName(stage: string): string {
  return stage
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function formatCapabilityType(type: string): string {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function formatBreakpointType(type: string): string {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function formatDate(dateString?: string): string {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  return date.toLocaleString()
}

function handleBack() {
  router.push('/missions')
}

async function handleRefresh() {
  await loadMissionDetails()
}

async function handleResume() {
  if (!workflow.value?.workflow_id) return
  isLoading.value = true
  try {
    await missionStore.resumeWorkflow(workflow.value.workflow_id)
    await loadMissionDetails()
  } catch (err) {
    console.error('Failed to resume:', err)
    error.value = 'Failed to resume workflow'
  } finally {
    isLoading.value = false
  }
}

async function handlePause() {
  if (!workflow.value?.workflow_id) return
  isLoading.value = true
  try {
    await missionStore.pauseWorkflow(workflow.value.workflow_id)
    await loadMissionDetails()
  } catch (err) {
    console.error('Failed to pause:', err)
    error.value = 'Failed to pause workflow'
  } finally {
    isLoading.value = false
  }
}

async function handleCancel() {
  if (!confirm('Are you sure you want to cancel this mission? This cannot be undone.')) return
  
  if (!missionId.value) return
  isLoading.value = true
  try {
    await missionStore.cancelMission(missionId.value)
    await loadMissionDetails()
  } catch (err) {
    console.error('Failed to cancel:', err)
    error.value = 'Failed to cancel mission'
  } finally {
    isLoading.value = false
  }
}

function handleBreakpointApproval() {
  if (pendingBreakpoints.value.length > 0) {
    currentBreakpoint.value = pendingBreakpoints.value[0]
    showBreakpointModal.value = true
  }
}

function handleBreakpointApproved() {
  showBreakpointModal.value = false
  currentBreakpoint.value = null
  loadMissionDetails()
}

function handleBreakpointRejected() {
  showBreakpointModal.value = false
  currentBreakpoint.value = null
  loadMissionDetails()
}

onMounted(async () => {
  await loadMissionDetails()

  // Set up auto-refresh every 5 seconds for active workflows
  if (workflow.value?.status === 'running') {
    refreshInterval.value = window.setInterval(() => {
      loadMissionDetails()
    }, 5000)
  }
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.mission-detail {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.back-button {
  margin-bottom: 1rem;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: #1e293b;
}

.status-tag {
  font-size: 1rem;
  padding: 0.5rem 1rem;
}

.mission-description {
  color: #64748b;
  margin: 0;
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

.detail-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.main-content,
.sidebar-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1e293b;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.progress-label {
  font-weight: 500;
  color: #334155;
}

.progress-value {
  font-weight: 700;
}

.progress-bar {
  margin-bottom: 1rem;
}

.current-stage {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1e293b;
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.75rem;
  color: #64748b;
}

.detail-value {
  font-size: 0.875rem;
  color: #1e293b;
}

.detail-value-bold {
  font-weight: 700;
}

.capability-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.capability-tag {
  padding: 0.5rem 0.75rem;
}

.breakpoint-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.breakpoint-list li {
  font-size: 0.875rem;
  color: #475569;
  padding-left: 1rem;
  position: relative;
}

.breakpoint-list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #3b82f6;
}

.mt-3 {
  margin-top: 0.75rem;
}

@media (max-width: 1024px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
