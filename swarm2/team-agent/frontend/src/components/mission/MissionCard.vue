<template>
  <Card class="mission-card" @click="handleClick">
    <template #content>
      <div class="card-header">
        <div class="mission-info">
          <div class="title-row">
            <h3 class="mission-title">{{ mission.mission_id }}</h3>
            <Tag :severity="statusSeverity">
              {{ workflow?.status || 'pending' }}
            </Tag>
          </div>
          <span class="created-date">
            Created {{ formatDate(workflow?.created_at) }}
          </span>
        </div>

        <Button
          icon="pi pi-ellipsis-v"
          text
          rounded
          size="small"
          @click.stop="handleOptionsClick"
          aria-label="More options"
        />
      </div>

      <p class="mission-description">
        {{ mission.description }}
      </p>

      <div class="mission-progress" v-if="workflow">
        <div class="progress-header">
          <span class="progress-label">Progress</span>
          <span class="progress-value">{{ workflow.progress }}%</span>
        </div>
        <ProgressBar :value="workflow.progress" :showValue="false" />
      </div>

      <div class="current-stage" v-if="workflow?.current_stage">
        <span class="stage-label">Current Stage</span>
        <Tag severity="info" class="stage-tag">
          {{ formatStageName(workflow.current_stage) }}
        </Tag>
      </div>

      <div class="mission-stats">
        <div class="stat-item">
          <span class="stat-label">Capabilities</span>
          <span class="stat-value">{{ mission.required_capabilities?.length || 0 }}</span>
        </div>

        <div class="stat-item">
          <span class="stat-label">Min Trust</span>
          <span class="stat-value">{{ mission.min_trust_score }}</span>
        </div>

        <div class="stat-item">
          <span class="stat-label">Breakpoints</span>
          <span class="stat-value">{{ mission.breakpoints?.length || 0 }}</span>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import type { MissionSpec, WorkflowStatus } from '@/types/mission.types'

const props = defineProps<{
  mission: MissionSpec
  workflow?: WorkflowStatus
}>()

const router = useRouter()

const statusSeverity = computed(() => {
  switch (props.workflow?.status) {
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

function formatDate(dateString?: string): string {
  if (!dateString) return 'Unknown'

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`

  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`

  return date.toLocaleDateString()
}

function formatStageName(stage: string): string {
  return stage
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function handleClick() {
  router.push(`/missions/${props.mission.mission_id}`)
}

function handleOptionsClick() {
  // TODO: Show options menu
  console.log('Options clicked for', props.mission.mission_id)
}
</script>

<style scoped>
.mission-card {
  cursor: pointer;
  transition: all 0.2s;
  height: 100%;
}

.mission-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border-color: #3b82f6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.mission-info {
  flex: 1;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.mission-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.created-date {
  font-size: 0.875rem;
  color: #64748b;
}

.mission-description {
  color: #475569;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.mission-progress {
  margin-bottom: 1rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.progress-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #334155;
}

.progress-value {
  font-size: 0.875rem;
  color: #64748b;
}

.current-stage {
  margin-bottom: 1rem;
}

.stage-label {
  font-size: 0.875rem;
  color: #64748b;
  display: block;
  margin-bottom: 0.25rem;
}

.stage-tag {
  font-size: 0.875rem;
}

.mission-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-weight: 700;
  font-size: 0.875rem;
  color: #1e293b;
}
</style>
