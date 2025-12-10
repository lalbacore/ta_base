<template>
  <div class="workflow-timeline">
    <h3 class="timeline-title">Workflow Progress</h3>

    <div v-if="stages.length === 0" class="empty-state">
      <p>No workflow stages yet</p>
    </div>

    <Timeline v-else :value="stages" class="custom-timeline">
      <template #marker="slotProps">
        <div class="timeline-marker" :class="`status-${slotProps.item.status}`">
          <ProgressSpinner
            v-if="slotProps.item.status === 'running'"
            style="width: 24px; height: 24px"
            strokeWidth="4"
          />
          <i v-else-if="slotProps.item.status === 'completed'" class="pi pi-check"></i>
          <i v-else-if="slotProps.item.status === 'failed'" class="pi pi-times"></i>
          <i v-else class="pi pi-circle"></i>
        </div>
      </template>

      <template #content="slotProps">
        <div class="stage-content">
          <div class="stage-header">
            <h4 class="stage-name">
              {{ formatStageName(slotProps.item.stage_name) }}
            </h4>
            <Tag :severity="getStatusSeverity(slotProps.item.status)">
              {{ slotProps.item.status }}
            </Tag>
          </div>

          <p class="stage-description">
            {{ getStageDescription(slotProps.item.stage_name) }}
          </p>

          <div class="stage-timestamps">
            <span v-if="slotProps.item.started_at">
              <i class="pi pi-clock"></i>
              Started: {{ formatTimestamp(slotProps.item.started_at) }}
            </span>
            <span v-if="slotProps.item.completed_at">
              <i class="pi pi-check-circle"></i>
              Completed: {{ formatTimestamp(slotProps.item.completed_at) }}
            </span>
            <span v-if="slotProps.item.started_at && slotProps.item.completed_at">
              <i class="pi pi-stopwatch"></i>
              Duration: {{ calculateDuration(slotProps.item.started_at, slotProps.item.completed_at) }}
            </span>
          </div>

  <div
            v-if="slotProps.item.optimization && debugMode"
            class="stage-optimization"
          >
            <div class="optimization-header">
              <span class="opt-label">Optimization Score</span>
              <span class="opt-value">{{ slotProps.item.optimization.score }}</span>
            </div>
            
            <div 
              class="math-equation"
              v-html="renderMath(slotProps.item.optimization.equation_md)"
            ></div>

            <div class="optimization-details">
              <div v-for="(comp, key) in slotProps.item.optimization.components" :key="key" class="opt-component">
                <span class="comp-key">{{ key }}</span>
                <span class="comp-val">
                  {{ comp.weight }} × {{ comp.value.toFixed(2) }} = <strong>{{ comp.contribution }}</strong>
                </span>
              </div>
            </div>
          </div>

          <div
            v-if="slotProps.item.output && slotProps.item.status === 'completed'"
            class="stage-output"
          >
            <div class="output-label">Output</div>
            <pre class="output-code">{{ JSON.stringify(slotProps.item.output, null, 2) }}</pre>
          </div>
        </div>
      </template>
    </Timeline>
  </div>
</template>

<script setup lang="ts">
import Timeline from 'primevue/timeline'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'
import type { WorkflowStage } from '@/types/mission.types'
import { computed } from 'vue'

const props = defineProps<{
  stages: WorkflowStage[],
  debugMode?: boolean
}>()

function renderMath(equation: string): string {
  if (!(window as any).katex) return equation
  try {
    return (window as any).katex.renderToString(equation, {
      throwOnError: false,
      displayMode: true
    })
  } catch (e) {
    return equation
  }
}

function formatStageName(stage: string): string {
  return stage
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function getStageDescription(stage: string): string {
  const descriptions: Record<string, string> = {
    'architect': 'Designing system architecture and component structure',
    'builder': 'Implementing the designed solution',
    'critic': 'Reviewing code quality and security',
    'governance': 'Validating compliance and policy adherence',
    'recorder': 'Recording workflow results and generating manifest',
    'initializing': 'Setting up workflow environment',
    'capability_selection': 'Selecting capabilities for execution'
  }
  return descriptions[stage] || 'Processing stage...'
}

function getStatusSeverity(status: string): string {
  switch (status) {
    case 'completed':
      return 'success'
    case 'running':
      return 'info'
    case 'failed':
      return 'danger'
    default:
      return 'secondary'
  }
}

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

function calculateDuration(start: string, end: string): string {
  const startDate = new Date(start)
  const endDate = new Date(end)
  const durationMs = endDate.getTime() - startDate.getTime()

  const seconds = Math.floor(durationMs / 1000)
  if (seconds < 60) return `${seconds}s`

  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  if (minutes < 60) return `${minutes}m ${remainingSeconds}s`

  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  return `${hours}h ${remainingMinutes}m`
}
</script>

<style scoped>
.workflow-timeline {
  padding: 1rem;
}

.timeline-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #1e293b;
}

.empty-state {
  padding: 3rem 1rem;
  text-align: center;
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  color: #64748b;
}

.timeline-marker {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
  box-shadow: 0 0 0 4px #ffffff;
}

.timeline-marker.status-completed {
  background-color: #10b981;
}

.timeline-marker.status-running {
  background-color: #3b82f6;
}

.timeline-marker.status-failed {
  background-color: #ef4444;
}

.timeline-marker.status-pending {
  background-color: #cbd5e1;
  color: #64748b;
}

.stage-content {
  padding-bottom: 2rem;
}

.stage-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.stage-name {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.stage-description {
  color: #64748b;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.stage-timestamps {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

.stage-timestamps span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stage-timestamps i {
  font-size: 0.75rem;
}

.stage-output {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}

.stage-optimization {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
}

.optimization-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #15803d;
}

.optimization-details {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #166534;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.opt-component {
  background: rgba(255,255,255,0.5);
  padding: 2px 6px;
  border-radius: 4px;
}

.comp-key {
  text-transform: capitalize;
  margin-right: 4px;
  color: #14532d;
}

.output-label {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #334155;
}

.output-code {
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  color: #1e293b;
}

:deep(.katex) {
  font-size: 1.1em;
}
</style>
